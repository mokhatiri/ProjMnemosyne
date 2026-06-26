"""In-process supervisor for the autonomous analyst.

The CLI analyst (`python -m analyst run`) is a *blocking* loop that `time.sleep`s
between generations -- fine for a terminal, but you can't watch it, hurry it, or
retune it from the browser. This supervisor runs the very same
:class:`analyst.engine.AnalysisEngine` generation loop on a background thread
that the frontend owns, driven by a :class:`threading.Event` instead of a bare
sleep. That single change is what makes the console controls possible:

    fast-forward / run-now   -> wake.set()        (ends the current wait instantly)
    pause / resume           -> a pause flag the loop checks each generation
    stop                     -> stop flag + wake   (loop exits, state saved)
    live progress + countdown-> in-memory counters the status endpoint reads
    retune (interval/grow/   -> runtime_config.json re-read at the top of every
       sources/queries...)      generation, so edits take effect next round
    new analyst (reset)      -> archive state+insights, start from generation 0

It reuses the engine's existing ``tick`` / state files unchanged, so a banked run
made by the CLI is picked up here and vice-versa (just don't run both at once --
they'd both write ``insights.jsonl``).

Concurrency: the frontend's HTTP server is single-threaded on purpose (the lower
layers keep module-level singletons). The only new concurrency is this thread vs
a request handler. :data:`WORK_LOCK` serializes the *heavy* layer-4/5 work (an
analyst tick, an /api/agent call) so the two never touch a reasoner/store at the
same time; the status endpoint only reads cached counters and never takes it, so
the UI stays responsive while a generation runs.
"""

import os
import time
import shutil
import logging
import threading
import importlib
import subprocess
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import sys

import layer5  # noqa: F401  (ensures the agents import cleanly at startup)
from analyst.config import Config as AnalystConfig
from analyst.engine import AnalysisEngine
from analyst import worklist, runtime_config

logger = logging.getLogger(__name__)

# project root = parent of the frontend package (where `python -m pipeline` runs)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORAGE = os.path.join(_ROOT, "storage")

# Serializes heavy layer4/5 work between the analyst thread and request handlers.
# Reentrant so a code path can nest acquisitions without deadlocking.
WORK_LOCK = threading.RLock()

# valid lifecycle phases (also documents the state machine)
PHASES = ("stopped", "growing", "analyzing", "sleeping", "idle", "paused")


class Supervisor:
    """Owns the analyst background thread and exposes thread-safe controls."""

    def __init__(self, offline_default: bool = False):
        self._offline_default = offline_default

        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()    # request the loop to exit
        self._wake = threading.Event()    # cut a wait short (run-now / config change / stop)
        self._paused = threading.Event()  # set => loop holds before the next generation
        self._slock = threading.Lock()    # guards the status fields below

        self.engine: Optional[AnalysisEngine] = None

        # --- status fields (read by status(), written by the loop) ---
        self.phase = "stopped"
        self.generation = 0
        self.tasks_done = 0
        self.tasks_total = 0
        self.tasks_pending = 0
        self.next_up: List[str] = []
        self.insights_banked = 0
        self.last_summary: Optional[dict] = None
        self.next_wake_epoch: Optional[float] = None
        self.started_at: Optional[float] = None
        self.last_error: Optional[str] = None

    # ======================================================================
    # status (cheap, lock-guarded reads -- never touches WORK_LOCK)
    # ======================================================================
    def _set(self, **fields) -> None:
        with self._slock:
            for k, v in fields.items():
                setattr(self, k, v)

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def status(self) -> Dict[str, Any]:
        running = self.is_running()
        # When stopped, the cached counters may be cold; refresh from disk once
        # (no tick can be running, so reading the graph here is safe).
        if not running and self.generation == 0 and self.last_summary is None:
            self._refresh_from_disk()
        with self._slock:
            secs = None
            if self.next_wake_epoch is not None:
                secs = max(0, round(self.next_wake_epoch - time.time()))
            return {
                "running": running,
                "phase": self.phase,
                "paused": self._paused.is_set(),
                "generation": self.generation,
                "tasks": {"done": self.tasks_done, "pending": self.tasks_pending,
                          "total": self.tasks_total},
                "next_up": list(self.next_up),
                "insights_banked": self.insights_banked,
                "last_summary": self.last_summary,
                "seconds_to_next": secs,
                "started_at": self.started_at,
                "last_error": self.last_error,
                "config": runtime_config.load(_STORAGE),
            }

    # ======================================================================
    # lifecycle controls (called from request handlers)
    # ======================================================================
    def start(self) -> Dict[str, Any]:
        if self.is_running():
            return {"ok": False, "error": "analyst already running"}
        self._stop.clear()
        self._wake.clear()
        self._paused.clear()
        self._set(last_error=None, started_at=time.time())
        self._thread = threading.Thread(target=self._loop, name="analyst-loop",
                                        daemon=True)
        self._thread.start()
        return {"ok": True, "message": "analyst started"}

    def pause(self) -> Dict[str, Any]:
        if not self.is_running():
            return {"ok": False, "error": "analyst not running"}
        self._paused.set()
        self._wake.set()   # break any current wait so it reaches the pause gate
        return {"ok": True, "message": "pausing after the current generation"}

    def resume(self) -> Dict[str, Any]:
        if not self.is_running():
            return {"ok": False, "error": "analyst not running"}
        self._paused.clear()
        self._wake.set()
        return {"ok": True, "message": "resumed"}

    def stop(self, timeout: float = 30.0) -> Dict[str, Any]:
        if not self.is_running():
            return {"ok": False, "error": "analyst not running"}
        self._stop.set()
        self._paused.clear()
        self._wake.set()
        self._thread.join(timeout=timeout)   # type: ignore[union-attr]
        stopped = not self.is_running()
        if stopped:
            self._set(phase="stopped", next_wake_epoch=None)
        return {"ok": stopped,
                "message": "stopped" if stopped
                else "stop requested; a long generation is still finishing"}

    def run_now(self) -> Dict[str, Any]:
        """Fast-forward: end the current wait so the next generation starts now."""
        if not self.is_running():
            return {"ok": False, "error": "analyst not running"}
        self._wake.set()
        return {"ok": True, "message": "running the next generation now"}

    def reset(self) -> Dict[str, Any]:
        """Archive the banked state+insights, then start fresh from generation 0.
        Refuses while running (stop first)."""
        if self.is_running():
            return {"ok": False, "error": "stop the analyst before resetting"}
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive = os.path.join(_STORAGE, "archive", stamp)
        moved = []
        for name in ("insights.jsonl", "analyst_state.json"):
            src = os.path.join(_STORAGE, name)
            if os.path.exists(src):
                os.makedirs(archive, exist_ok=True)
                shutil.move(src, os.path.join(archive, name))
                moved.append(name)
        self._set(generation=0, tasks_done=0, tasks_pending=0, tasks_total=0,
                  next_up=[], insights_banked=0, last_summary=None,
                  last_error=None)
        self._refresh_from_disk()
        return {"ok": True,
                "message": (f"archived {', '.join(moved)} to storage/archive/{stamp}; "
                            "fresh analyst ready") if moved
                else "nothing to archive; fresh analyst ready",
                "archive": f"storage/archive/{stamp}" if moved else None}

    def update_config(self, incoming: Dict[str, Any]) -> Dict[str, Any]:
        """Persist new runtime config; the loop re-reads it next generation.
        Wakes a sleeping loop so a shorter interval / new grow takes effect now."""
        saved = runtime_config.save(incoming, _STORAGE)
        if self.is_running():
            self._wake.set()
        return {"ok": True, "config": saved}

    # ======================================================================
    # the loop (runs on the background thread)
    # ======================================================================
    def _loop(self) -> None:
        try:
            cfg = runtime_config.load(_STORAGE)
            aconf = AnalystConfig()
            aconf.batch_size = cfg["batch_size"]
            self.engine = AnalysisEngine(aconf, offline=cfg["offline"])

            state = self.engine._load_state()
            done: Set[str] = set(state.get("done_task_ids", []))
            known: Set[str] = self.engine._known_insight_ids()
            gen = state.get("iteration", 0)
            self._refresh_tasks(done, gen, len(known))

            while not self._stop.is_set():
                if self._paused.is_set():
                    self._gate_paused()
                    if self._stop.is_set():
                        break

                cfg = runtime_config.load(_STORAGE)        # live retune point
                self.engine.config.batch_size = cfg["batch_size"]
                self.engine.offline = cfg["offline"]
                gen += 1

                if cfg.get("grow", 0) > 0:
                    self._set(phase="growing")
                    self._grow(cfg)
                    self._invalidate_caches()

                self._set(phase="analyzing")
                with WORK_LOCK:
                    summary = self.engine.tick(gen, done, known)
                self.engine._save_state(gen, done)
                self._set(last_summary=summary)
                self._refresh_tasks(done, gen, len(known))

                # nothing left and not growing -> idle until told to do something
                if summary["pending_after"] == 0 and not cfg.get("grow", 0):
                    self._wait_idle()
                    continue

                self._wait_interval(cfg["interval_seconds"])
        except Exception as exc:                            # never die silently
            logger.exception("analyst loop crashed")
            self._set(last_error=f"{type(exc).__name__}: {exc}")
        finally:
            self._set(phase="stopped", next_wake_epoch=None)

    # --- loop helpers ----------------------------------------------------
    def _gate_paused(self) -> None:
        self._set(phase="paused", next_wake_epoch=None)
        while self._paused.is_set() and not self._stop.is_set():
            self._wake.wait(timeout=1.0)
            self._wake.clear()

    def _wait_interval(self, seconds: int) -> None:
        if seconds <= 0:
            return
        self._set(phase="sleeping", next_wake_epoch=time.time() + seconds)
        self._wake.wait(timeout=seconds)
        self._wake.clear()
        self._set(next_wake_epoch=None)

    def _wait_idle(self) -> None:
        """All current tasks done and not growing: hold (cheaply) until the user
        hits run-now, edits the config, pauses, or stops."""
        self._set(phase="idle", next_wake_epoch=None)
        while not self._stop.is_set() and not self._paused.is_set():
            if self._wake.wait(timeout=2.0):
                self._wake.clear()
                break   # woken by run-now / config change -> do another generation

    def _grow(self, cfg: Dict[str, Any]) -> None:
        """Fetch + process N new papers via the pipeline (subprocess, no UI),
        using the configured sources and per-source query overrides."""
        n = cfg["grow"]
        sources = cfg.get("sources") or ["arxiv"]
        queries = cfg.get("queries") or {}
        logger.info("growing corpus: ingesting %d paper(s) from %s", n, ", ".join(sources))
        argv = [sys.executable, "-m", "pipeline", "--ingest", str(n),
                "--sources", *sources, "--limit", str(cfg.get("limit", 5)),
                "--no-serve"]
        for src in sources:
            q = queries.get(src)
            if q:
                argv += ["--query", f"{src}={q}"]
        if cfg.get("offline"):
            argv.append("--offline")
        try:
            subprocess.run(argv, cwd=_ROOT, check=False)
        except Exception:
            logger.exception("grow step failed; continuing with the existing corpus")

    @staticmethod
    def _invalidate_caches() -> None:
        """After growing, drop the lower layers' in-memory singletons so the
        agents this generation see the newly-indexed papers (not a stale store)."""
        with WORK_LOCK:
            for mod in ("layer3-1.search", "layer3-2.queries"):
                try:
                    importlib.import_module(mod).reload()
                except Exception:
                    logger.warning("could not reload %s after grow", mod)
            try:
                import layer4.tools as tools
                tools._all_chunks.cache_clear()
            except Exception:
                logger.warning("could not clear layer4 keyword-chunk cache")

    # --- counters --------------------------------------------------------
    def _refresh_tasks(self, done: Set[str], gen: int, banked: int) -> None:
        """Recompute the to-do counts from the (current) knowledge graph. Called
        only from the loop thread; the graph it reads is already loaded."""
        try:
            tasks = worklist.build_tasks(worklist.graph_method_labels())
        except Exception:
            logger.exception("could not rebuild task list")
            tasks = []
        pending = [t for t in tasks if t.id not in done]
        self._set(generation=gen, tasks_total=len(tasks), tasks_done=len(done),
                  tasks_pending=len(pending), next_up=[t.id for t in pending[:5]],
                  insights_banked=banked)

    def _refresh_from_disk(self) -> None:
        """Cold-start snapshot for status() when stopped: read the state +
        insights files (cheap) and the task list (safe -- no tick running)."""
        eng = AnalysisEngine(AnalystConfig(), offline=self._offline_default)
        state = eng._load_state()
        done = set(state.get("done_task_ids", []))
        banked = len(eng._known_insight_ids())
        with WORK_LOCK:
            self._refresh_tasks(done, state.get("iteration", 0), banked)


# Module-level singleton the server imports. offline default is set by run().
supervisor = Supervisor()
