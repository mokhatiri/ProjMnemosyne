"""Layer 6 (A2A Coordination) CLI.

Investigates a topic by running all the Layer 5 agents and cross-validating
their structured findings into a single consolidated Report.

Run from the project root (the folder containing `layer6/`):

    python -m layer6 investigate "chain of thought" --offline
    python -m layer6 investigate "supervised fine-tuning"
    python -m layer6 investigate "chain of thought" --no-save

Uses the real HF reasoner when HF_TOKEN is set, and the offline stub under
--offline (or automatically when no key is present).
"""

import sys
import json
import argparse
import logging
from dataclasses import asdict

# Load API tokens from a .env file in the project root if present (see the
# other layers' CLIs). Optional; shell-set vars win.
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from .config import Config
from .coordinator import Coordinator

# Same Windows-console fix as the other layers.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def save_report(config: Config, report) -> None:
    import os
    os.makedirs(config.local_storage_path, exist_ok=True)
    with open(config.reports_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(report), ensure_ascii=False) + "\n")


def cmd_investigate(args: argparse.Namespace) -> None:
    config = Config()
    report = Coordinator(config=config, offline=args.offline).investigate(
        args.topic, k=args.k)

    print(f"\n=== A2A report on {args.topic!r} ===")
    print(report.summary)

    print("\n--- findings ---")
    for f in report.findings:
        flag = " [stub]" if f.get("stub") else ""
        print(f"  [{f['kind']}] {f['confidence']}{flag}  {f['summary']}")

    print("\n--- cross-validation links ---")
    if report.cross_validations:
        for c in report.cross_validations:
            print(f"  ({c['type']}) {c['note']}")
            print(f"     links: {', '.join(c['finding_ids'])}")
    else:
        print("  (none -- agents' findings did not corroborate on this topic)")

    if args.no_save:
        print("\n(--no-save: nothing written)")
    else:
        save_report(config, report)
        print(f"\nsaved report {report.id} to {config.reports_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m layer6", description="Layer 6 A2A coordination")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("investigate", help="run all agents on a topic + cross-validate")
    p.add_argument("topic", help="the topic/proposition to investigate")
    p.add_argument("-k", type=int, default=None, help="units gathered per probe")
    p.add_argument("--offline", action="store_true",
                   help="use the stub reasoner (no HF_TOKEN needed)")
    p.add_argument("--no-save", action="store_true",
                   help="don't append the report to reports.jsonl")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    if args.command == "investigate":
        cmd_investigate(args)


if __name__ == "__main__":
    main()
