"""Layer 5 (Analytical Agent Layer) CLI.

Runs the specialized agents over the knowledge graph + retrieval (via the
Layer 4 tools) and prints/saves their structured Findings.

Run from the project root (the folder containing `layer5/`):

    python -m layer5 list                              # the available agents
    python -m layer5 run contradiction --topic "chain of thought"
    python -m layer5 run synergy
    python -m layer5 run gap
    python -m layer5 run evidence --topic "supervised fine-tuning"
    python -m layer5 run all --topic "chain of thought" --offline
    python -m layer5 run all --no-save                 # don't append to findings.jsonl

The reasoning agents (synergy/evidence) and Layer 4's LLM tools use the real
HF model when HF_TOKEN is set, and a clearly-labelled offline stub under
--offline (or automatically when no key is present).
"""

import sys
import json
import argparse
import logging
from dataclasses import asdict

# Load API tokens from a .env file in the project root if present, so secrets
# (HF_TOKEN, VOYAGE_API_KEY, S2_API_KEY) can live there instead of being
# exported in every shell. Shell-set vars take precedence (load_dotenv never
# overrides os.environ); python-dotenv is optional -- if it isn't installed,
# the .env is simply ignored.
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from .config import Config
from .base import save_findings
from .agents import AGENTS, run_agent, run_all

# Same Windows-console fix as the other layers.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def cmd_list() -> None:
    print(f"\n=== {len(AGENTS)} analytical agents ===")
    for name, cls in AGENTS.items():
        summary = " ".join((cls.__doc__ or "").split())
        print(f"\n{name}")
        print(f"  {summary[:300]}")


def cmd_run(args: argparse.Namespace) -> None:
    config = Config()
    if args.agent == "all":
        findings = run_all(topic=args.topic, k=args.k, offline=args.offline, config=config)
    else:
        findings = run_agent(args.agent, topic=args.topic, k=args.k,
                             offline=args.offline, config=config)

    print(f"\n=== {args.agent}: {len(findings)} finding(s) ===")
    for f in findings:
        flag = " [stub]" if f.stub else ""
        print(f"\n[{f.kind}] {f.confidence}{flag}  {f.summary}")
        if f.provenance:
            print(f"  provenance: {', '.join(p for p in f.provenance if p)}")
    if findings:
        print("\n--- full findings (JSON) ---")
        print(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2))

    if args.no_save:
        print("\n(--no-save: nothing written)")
    else:
        save_findings(config, findings)
        print(f"\nappended {len(findings)} finding(s) to {config.findings_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m layer5", description="Layer 5 analytical agents")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list the available agents")

    p_run = sub.add_parser("run", help="run an agent (or 'all')")
    p_run.add_argument("agent", choices=[*AGENTS, "all"],
                       help="which agent to run")
    p_run.add_argument("--topic", default=None,
                       help="seed topic/proposition (agents auto-scan if omitted)")
    p_run.add_argument("-k", type=int, default=None,
                       help="how many units to gather per probe")
    p_run.add_argument("--offline", action="store_true",
                       help="use the stub reasoner (no HF_TOKEN needed)")
    p_run.add_argument("--no-save", action="store_true",
                       help="don't append findings to findings.jsonl")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    if args.command == "list":
        cmd_list()
    elif args.command == "run":
        cmd_run(args)


if __name__ == "__main__":
    main()
