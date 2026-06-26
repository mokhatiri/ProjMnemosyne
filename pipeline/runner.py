"""Run the whole stack end-to-end, then launch the frontend.

Each build step is the corresponding layer's own CLI, run as a subprocess
(`python -m layerX ...`). Running them as subprocesses -- rather than importing
each layer's internals -- means this orchestrator stays decoupled from every
layer's API, shows each layer's own logging live, and naturally handles the
hyphenated package names and per-layer flags. The build steps are all
idempotent / append-only, so re-running the pipeline is cheap and safe.

The final step, serving the frontend, runs **in-process** (it's the blocking
"now use it" step, so there's no reason to spawn another interpreter for it).

Key-awareness: extraction (L2) needs HF_TOKEN and embeddings (L3-1) need
VOYAGE_API_KEY. When a key is absent the orchestrator skips or falls back
(fake embeddings) with a clear note instead of failing -- the corpus already on
disk is reused. Everything still ends at a usable, served console.
"""

import os
import sys
import time
import logging
import subprocess
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# the project root = parent of this package, so subprocesses run from there
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _banner(text: str) -> None:
    line = "=" * 70
    print(f"\n{line}\n== {text}\n{line}")


def _step(label: str, argv: List[str]) -> str:
    """Run one `python -m ...` step. Returns 'ok' | 'failed'."""
    _banner(f"{label}   ($ python {' '.join(argv)})")
    start = time.monotonic()
    proc = subprocess.run([sys.executable, *argv], cwd=_ROOT)
    dt = time.monotonic() - start
    status = "ok" if proc.returncode == 0 else "failed"
    print(f"\n-- {label}: {status} ({dt:.1f}s, exit {proc.returncode})")
    return status


def run_pipeline(*, ingest: int = 0, sources: Optional[List[str]] = None,
                 queries: Optional[Dict[str, str]] = None,
                 limit: Optional[int] = None, skip_extract: bool = False,
                 skip_index: bool = False, skip_graph: bool = False,
                 fake_embeddings: bool = False, offline: bool = False,
                 investigate: Optional[str] = None, serve: bool = True,
                 host: str = "127.0.0.1", port: int = 8000,
                 keep_going: bool = False) -> int:
    """Drive the full pipeline. Returns a process exit code (0 = all good)."""
    has_hf = bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN"))
    has_voyage = bool(os.environ.get("VOYAGE_API_KEY"))
    limit_args = ["--limit", str(limit)] if limit else []
    results = []   # (label, status) for the closing summary

    def record(label, status):
        results.append((label, status))
        return status

    # --- L1: ingestion (opt-in: needs network + optionally GROBID) ------------
    if ingest > 0:
        src = sources or ["arxiv"]
        argv = ["-m", "layer1", "--sources", *src,
                "--ingest", str(ingest)] + (["--limit", str(limit)] if limit else [])
        # per-source query overrides -> layer1's repeatable --query SOURCE=Q flag
        for name, query in (queries or {}).items():
            if name in src and query:
                argv += ["--query", f"{name}={query}"]
        if record("L1 ingest", _step("Layer 1 - data ingestion", argv)) == "failed" \
                and not keep_going:
            return _finish(results, served=False, code=1)
    else:
        record("L1 ingest", "skipped (use --ingest N to fetch papers)")

    # --- L2: knowledge extraction (needs HF_TOKEN) ----------------------------
    if skip_extract:
        record("L2 extract", "skipped (--skip-extract)")
    elif not has_hf:
        record("L2 extract",
               "skipped (no HF_TOKEN; reusing existing extracted.jsonl)")
    elif record("L2 extract", _step("Layer 2 - knowledge extraction",
                                    ["-m", "layer2", *limit_args])) == "failed" \
            and not keep_going:
        return _finish(results, served=False, code=1)

    # --- L3-1: embedding + index (needs VOYAGE_API_KEY, else fake) ------------
    if skip_index:
        record("L3-1 index", "skipped (--skip-index)")
    else:
        use_fake = fake_embeddings or not has_voyage
        argv = ["-m", "layer3-1", "index", *limit_args]
        if use_fake:
            argv.append("--fake-embeddings")
        note = " (fake embeddings)" if use_fake else ""
        if record("L3-1 index" + note,
                  _step("Layer 3-1 - embedding & index" + note, argv)) == "failed" \
                and not keep_going:
            return _finish(results, served=False, code=1)

    # --- L3-2: knowledge graph (no keys needed) -------------------------------
    if skip_graph:
        record("L3-2 graph", "skipped (--skip-graph)")
    elif record("L3-2 graph", _step("Layer 3-2 - knowledge graph",
                                    ["-m", "layer3-2", "build"])) == "failed" \
            and not keep_going:
        return _finish(results, served=False, code=1)

    # --- L6: optional A2A investigation as part of the run --------------------
    if investigate:
        argv = ["-m", "layer6", "investigate", investigate]
        if offline:
            argv.append("--offline")
        record("L6 investigate", _step("Layer 6 - A2A investigation", argv))

    # --- serve the frontend (in-process, blocking) ----------------------------
    if not serve:
        _finish(results, served=False, code=0)
        print(f"\n(--no-serve) Build done. Launch the console with:\n"
              f"   python -m frontend --host {host} --port {port}"
              f"{' --offline' if offline else ''}")
        return 0

    _finish(results, served=True, code=0)
    _banner("Layer 4-6 + frontend - serving console")
    import frontend                       # in-process: this call blocks
    frontend.run(host=host, port=port, offline=offline)
    return 0


def _finish(results, *, served: bool, code: int) -> int:
    """Print the per-step summary."""
    _banner("pipeline summary")
    for label, status in results:
        mark = "OK  " if status == "ok" else ("--  " if status.startswith("skip") else "FAIL")
        print(f"  [{mark}] {label}: {status}")
    if not served and code == 0:
        print("\nbuild steps complete.")
    elif code != 0:
        print("\na step failed; stopped before serving (use --keep-going to override).")
    return code
