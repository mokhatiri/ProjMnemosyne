"""The autonomous analysis loop.

Each *generation* the engine:
  1. (optionally) grows the corpus by running the pipeline's ingest+build,
  2. re-derives its to-do list from the knowledge graph (so new papers create
     new work automatically),
  3. takes the next small batch of not-yet-done tasks,
  4. runs the matching Layer 5 agent on each, turning out Findings,
  5. scores each finding, drops duplicates it has already recorded, and appends
     the genuinely new ones to storage/insights.jsonl, and
  6. saves its state (which tasks are done, which insights are known, the
     generation counter) so it resumes exactly where it left off after a stop.

Then it sleeps for the configured interval and does it again -- slowly, forever
(or for a bounded number of generations), without anyone driving it. Stop it
with Ctrl+C; state is saved so the next run continues.

Insights are *ranked*: a finding's score rewards higher confidence, broader
provenance (more distinct papers), and real (non-stub) reasoning -- so the most
interesting results float to the top of `analyst insights`.
"""

import os
import sys
import json
import time
import logging
import subprocess
from dataclasses import asdict
from typing import Dict, List, Optional, Set

import layer5   # normal import (no hyphen): the analytical agents
import verifier  # deterministic checks run before an insight is banked

from .config import Config
from . import worklist

logger = logging.getLogger(__name__)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONF_SCORE = {"high": 3.0, "medium": 2.0, "low": 1.0}


class AnalysisEngine:
    """Runs the analytical agents on a self-directed loop and banks insights."""

    def __init__(self, config: Optional[Config] = None, offline: bool = False):
        self.config = config or Config()
        self.offline = offline

    # --- scoring ---------------------------------------------------------------
    @staticmethod
    def _score(finding: dict) -> float:
        """Higher = more worth a human's attention."""
        conf = _CONF_SCORE.get(finding.get("confidence"), 1.0)
        papers = len({p for p in finding.get("provenance", [])
                      if p and "#" not in p
                      and not p.startswith(("method:", "dataset:"))})
        real_bonus = 0.0 if finding.get("stub") else 2.0
        return round(conf + 0.5 * papers + real_bonus, 2)

    # --- state + insight persistence ------------------------------------------
    def _load_state(self) -> dict:
        if os.path.exists(self.config.state_path):
            with open(self.config.state_path, encoding="utf-8") as fh:
                return json.load(fh)
        return {"iteration": 0, "done_task_ids": []}

    def _save_state(self, iteration: int, done: Set[str]) -> None:
        os.makedirs(self.config.local_storage_path, exist_ok=True)
        with open(self.config.state_path, "w", encoding="utf-8") as fh:
            json.dump({"iteration": iteration, "done_task_ids": sorted(done)}, fh, indent=2)

    def _known_insight_ids(self) -> Set[str]:
        """Ids already banked or already rejected (so neither is redone)."""
        ids: Set[str] = set()
        for path in (self.config.insights_path, self.config.rejected_path):
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            ids.add(json.loads(line)["id"])
                        except (json.JSONDecodeError, KeyError):
                            pass
        return ids

    def _load_gate(self):
        """(corpus, pairs of the already banked insights that pass), or
        (None, None) when the gate is off or the corpus is not indexed yet."""
        if not self.config.verify:
            return None, None
        try:
            corpus = verifier.Corpus.load(self.config.corpus_storage_path)
        except FileNotFoundError:
            logger.warning("verification skipped: no chunks.jsonl yet (run layer3-1 index)")
            return None, None
        seen: Set[tuple] = set()
        if os.path.exists(self.config.insights_path):
            with open(self.config.insights_path, encoding="utf-8") as fh:
                verifier.check_all([json.loads(l) for l in fh if l.strip()], corpus, seen)
        return corpus, seen

    def _append_insights(self, insights: List[dict], path: Optional[str] = None) -> None:
        if not insights:
            return
        os.makedirs(self.config.local_storage_path, exist_ok=True)
        with open(path or self.config.insights_path, "a", encoding="utf-8") as fh:
            for ins in insights:
                fh.write(json.dumps(ins, ensure_ascii=False) + "\n")

    # --- optional corpus growth (truly hands-off mode) ------------------------
    def _grow(self, n: int) -> None:
        """Fetch + process n new papers by invoking the pipeline build (no UI).
        Heavy/network/LLM -- only runs when --grow is given."""
        logger.info("growing corpus: ingesting %d paper(s) via the pipeline", n)
        subprocess.run([sys.executable, "-m", "pipeline", "--ingest", str(n),
                        "--no-serve"], cwd=_ROOT)

    # --- one generation --------------------------------------------------------
    def tick(self, iteration: int, done: Set[str], known_ids: Set[str]) -> dict:
        """Run one batch of pending tasks; return a summary dict."""
        tasks = worklist.build_tasks(worklist.graph_method_labels())
        pending = [t for t in tasks if t.id not in done]
        batch = pending[: self.config.batch_size]

        new_insights: List[dict] = []
        rejected: List[dict] = []
        corpus, seen = self._load_gate()
        for task in batch:
            try:
                findings = layer5.run_agent(task.agent, topic=task.topic,
                                            k=self.config.default_k,
                                            offline=self.offline)
            except Exception:   # one bad task must not stop the loop
                logger.exception("task %s failed", task.id)
                done.add(task.id)
                continue
            for f in findings:
                d = asdict(f)
                if d["id"] in known_ids:   # already banked (dedup across generations)
                    continue
                known_ids.add(d["id"])
                d["_score"] = self._score(d)
                d["_first_seen_generation"] = iteration
                if corpus is not None:
                    v = verifier.check(d, corpus, seen)
                    d["_verified"] = v.passed
                    if v.warnings:
                        d["_warnings"] = v.warnings
                    if not v.passed:
                        d["_errors"] = v.errors
                        rejected.append(d)
                        continue
                new_insights.append(d)
            done.add(task.id)

        self._append_insights(new_insights)
        self._append_insights(rejected, self.config.rejected_path)
        return {"ran": len(batch), "pending_after": len(pending) - len(batch),
                "new_insights": len(new_insights), "rejected": len(rejected),
                "total_tasks": len(tasks)}

    # --- the loop --------------------------------------------------------------
    def run(self, iterations: Optional[int] = None, interval: Optional[int] = None,
            grow: int = 0) -> None:
        """Loop forever (or for `iterations` generations), slowly."""
        interval = self.config.interval_seconds if interval is None else interval
        state = self._load_state()
        done: Set[str] = set(state.get("done_task_ids", []))
        known_ids = self._known_insight_ids()
        gen = state.get("iteration", 0)

        print(f"autonomous analyst starting (offline={self.offline}, "
              f"interval={interval}s, batch={self.config.batch_size}). "
              f"Resuming at generation {gen}; {len(done)} task(s) already done, "
              f"{len(known_ids)} insight(s) seen (banked + rejected). Ctrl+C to stop.")

        completed = 0
        try:
            while iterations is None or completed < iterations:
                gen += 1
                completed += 1
                if grow:
                    self._grow(grow)
                summary = self.tick(gen, done, known_ids)
                self._save_state(gen, done)
                print(f"\n[gen {gen}] ran {summary['ran']} task(s), "
                      f"{summary['new_insights']} new insight(s), "
                      f"{summary['rejected']} rejected by the verifier; "
                      f"{summary['pending_after']} task(s) pending "
                      f"(of {summary['total_tasks']}); "
                      f"{len(known_ids)} insight(s) seen so far (banked + rejected).")

                # nothing left and not growing the corpus -> the analyst is done
                if summary["pending_after"] == 0 and not grow:
                    print("\nAll current analysis tasks complete. Add papers "
                          "(python -m pipeline --ingest N) to give the analyst "
                          "more to chew on, or pass --grow N to do it in-loop.")
                    break

                last = (iterations is not None and completed >= iterations)
                if not last and interval > 0:
                    print(f"sleeping {interval}s until the next generation...")
                    time.sleep(interval)
        except KeyboardInterrupt:
            print("\nstopped. State saved; rerun to resume where you left off.")
            self._save_state(gen, done)
