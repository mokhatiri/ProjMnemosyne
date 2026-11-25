"""Retrieval evaluation CLI.

Run from the project root:

    python -m evaluation                 # report on ./storage
    python -m evaluation --k 3           # recall@3 instead of recall@5
    python -m evaluation --json          # machine-readable output
    python -m evaluation --storage DIR   # evaluate another store

Offline: reads storage/vectors.npy + chunks.jsonl, makes no API calls.
"""

import argparse
import json
import sys

from .retrieval import run


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="python -m evaluation",
                                     description="Offline retrieval evaluation (recall@k, MRR).")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--storage", default=None, help="storage folder (default ./storage)")
    parser.add_argument("--json", action="store_true", help="print the full result as JSON")
    args = parser.parse_args()

    res = run(args.storage, args.k)
    if args.json:
        print(json.dumps(res, indent=2))
        return 0

    k = args.k
    base = res["random_baseline"]
    print(f"Task        : {res['task']}")
    print(f"Model       : {res['model']}")
    print(f"Queries     : {res['queries']} units, {res['candidates']} candidate papers")
    print(f"recall@1    : {res['recall@1']:.3f}")
    print(f"recall@{k}    : {res[f'recall@{k}']:.3f}   (random: {base['recall_at_k']:.3f})")
    print(f"MRR         : {res['mrr']:.3f}   (random: {base['mrr']:.3f})")
    print("By unit kind:")
    for kind, r in res["by_kind"].items():
        print(f"  {kind:<11} n={r['queries']:<3} recall@{k}={r[f'recall@{k}']:.3f}  MRR={r['mrr']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
