"""Layer 2 (Knowledge Extraction) CLI.

Reads the papers Layer 1 ingested (storage/metadata.jsonl), extracts
structured scientific units (claims, methods, datasets, results, assumptions,
limitations) with an open model on the Hugging Face Inference API, and appends
them to storage/extracted.jsonl. Already-extracted papers are skipped, so
re-running is always safe.

Run from the project root (the folder containing `layer2/`):

    python -m layer2                        # extract everything pending
    python -m layer2 --limit 2              # at most 2 papers
    python -m layer2 --paper-id arxiv:2606.11189v1
    python -m layer2 --dry-run              # print prompts, no API calls
    python -m layer2 --model Qwen/Qwen2.5-72B-Instruct

Needs HF_TOKEN (a Hugging Face access token with inference permission) in the
environment (except with --dry-run).
"""

import sys
import argparse
import logging

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
from .pipeline import run

# Paper text is full of non-Latin-1 characters (Greek letters, math symbols).
# Windows consoles default to a legacy codepage (cp1252) that can't print
# them, so force UTF-8 on stdout/stderr -- replacing anything truly unprintable
# rather than crashing mid-run.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Layer 2 knowledge-extraction pipeline")
    parser.add_argument(
        "--limit", type=int, default=None, metavar="N",
        help="Extract at most N pending papers (default: all).")
    parser.add_argument(
        "--paper-id", default=None, metavar="ID",
        help="Extract a single paper by its id, e.g. arxiv:2606.11189v1")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse TEI and print the prompts that would be sent, "
             "without calling the API (no key required).")
    parser.add_argument(
        "--model", default=None, metavar="MODEL",
        help="Override the Hugging Face model id (default: config/LAYER2_MODEL env).")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    config = Config()
    if args.model:
        config.model = args.model
    run(config, limit=args.limit, paper_id=args.paper_id, dry_run=args.dry_run)


if __name__ == "__main__":
    print("\n=== Starting Layer 2 Knowledge Extraction Pipeline ===\n")
    main()
    print("\n=== Layer 2 Knowledge Extraction Pipeline Complete ===\n")
