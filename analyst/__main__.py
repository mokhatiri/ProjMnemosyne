"""Autonomous analyst CLI.

The hands-off analysis loop over the corpus. Build the corpus first
(`python -m pipeline`), then let the analyst run:

    python -m analyst run                       # loop forever, slowly (15-min gap)
    python -m analyst run --iterations 3        # just 3 generations, then stop
    python -m analyst run --interval 60         # faster cadence
    python -m analyst run --grow 2              # also fetch 2 new papers each generation
    python -m analyst run --offline             # stub reasoner (no HF_TOKEN)
    python -m analyst insights --top 15         # show the highest-ranked insights so far
    python -m analyst status                    # progress + pending work

It self-selects what to analyze from the knowledge graph, accumulates ranked
insights in storage/insights.jsonl, and saves state so it resumes after a stop.
"""

import sys
import json
import argparse
import logging

# Load API tokens from .env (so real reasoning/embeddings are used when present).
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from .config import Config
from .engine import AnalysisEngine

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def cmd_run(args) -> None:
    AnalysisEngine(Config(), offline=args.offline).run(
        iterations=args.iterations, interval=args.interval, grow=args.grow)


def _load_insights(config: Config) -> list:
    import os
    if not os.path.exists(config.insights_path):
        return []
    out = []
    with open(config.insights_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def cmd_insights(args) -> None:
    config = Config()
    insights = _load_insights(config)
    insights.sort(key=lambda d: d.get("_score", 0), reverse=True)
    shown = insights[: args.top]
    print(f"\n=== top {len(shown)} of {len(insights)} banked insight(s) ===")
    for d in shown:
        flag = " [stub]" if d.get("stub") else ""
        print(f"\n[{d.get('_score')}] [{d['kind']}] {d['confidence']}{flag} "
              f"(gen {d.get('_first_seen_generation')})")
        print(f"  {d['summary']}")
        prov = [p for p in d.get("provenance", []) if p]
        if prov:
            print(f"  provenance: {', '.join(prov)}")


def cmd_status(args) -> None:
    config = Config()
    insights = _load_insights(config)
    from . import worklist
    import os
    state = {}
    if os.path.exists(config.state_path):
        with open(config.state_path, encoding="utf-8") as fh:
            state = json.load(fh)
    done = set(state.get("done_task_ids", []))
    tasks = worklist.build_tasks(worklist.graph_method_labels())
    pending = [t for t in tasks if t.id not in done]
    print("\n=== analyst status ===")
    print(f"generation:      {state.get('iteration', 0)}")
    print(f"tasks done:      {len(done)} / {len(tasks)}")
    print(f"tasks pending:   {len(pending)}")
    print(f"insights banked: {len(insights)}")
    if pending:
        print("next up: " + ", ".join(t.id for t in pending[:5])
              + (" ..." if len(pending) > 5 else ""))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="python -m analyst",
                                description="Autonomous research analyst loop")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="run the analysis loop")
    r.add_argument("--iterations", type=int, default=None,
                   help="number of generations to run (default: forever)")
    r.add_argument("--interval", type=int, default=None,
                   help="seconds between generations (default: config, 900)")
    r.add_argument("--grow", type=int, default=0, metavar="N",
                   help="fetch+process N new papers each generation (in-loop)")
    r.add_argument("--offline", action="store_true",
                   help="use the stub reasoner (no HF_TOKEN needed)")

    i = sub.add_parser("insights", help="show the highest-ranked insights so far")
    i.add_argument("--top", type=int, default=15)

    sub.add_parser("status", help="show progress and pending work")
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    {"run": cmd_run, "insights": cmd_insights, "status": cmd_status}[args.command](args)


if __name__ == "__main__":
    main()
