"""Verify banked insights.

    python -m verifier                      # report on storage/insights.jsonl
    python -m verifier --details            # also list every failure reason
    python -m verifier --json out.json      # per-insight verdicts as JSON
"""

import argparse
import json
import os
import sys
from collections import defaultdict

from .checks import Corpus, check_all


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="python -m verifier")
    ap.add_argument("--storage", default="./storage")
    ap.add_argument("--insights", default=None, help="default: <storage>/insights.jsonl")
    ap.add_argument("--details", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    path = args.insights or os.path.join(args.storage, "insights.jsonl")
    with open(path, encoding="utf-8") as fh:
        insights = [json.loads(l) for l in fh if l.strip()]
    verdicts = check_all(insights, Corpus.load(args.storage))

    by = defaultdict(lambda: [0, 0, 0])   # kind -> [total, passed, real-and-passed]
    for ins, v in zip(insights, verdicts):
        row = by[v.kind]
        row[0] += 1
        row[1] += v.passed
        row[2] += v.passed and not ins.get("stub")
    total = len(verdicts)
    passed = sum(v.passed for v in verdicts)
    real = sum(1 for i in insights if not i.get("stub"))
    real_passed = sum(1 for i, v in zip(insights, verdicts) if v.passed and not i.get("stub"))
    print(f"Insights checked : {total} ({real} from the LLM reasoner, {total - real} from the offline stub)")
    print(f"Pass (no error)  : {passed}/{total} = {passed / max(total, 1):.0%}")
    print(f"LLM insights pass: {real_passed}/{real} = {real_passed / max(real, 1):.0%}")
    print("By kind (total / pass / LLM-and-pass):")
    for kind, (t, p, rp) in sorted(by.items()):
        print(f"  {kind:<14} {t:>3} / {p:>3} / {rp:>3}")
    reasons = defaultdict(int)
    for v in verdicts:
        for e in v.errors:
            reasons[e.split(":")[0] if e.startswith(("claim_", "supporting", "contradicting", "method_"))
                    else e.split("(")[0].split("'")[0].strip()] += 1
    if reasons:
        print("Most common errors:")
        for r, n in sorted(reasons.items(), key=lambda x: -x[1])[:8]:
            print(f"  {n:>3} x {r}")
    if args.details:
        for ins, v in zip(insights, verdicts):
            if v.errors or v.warnings:
                print(f"\n{v.insight_id} [{v.kind}] {'PASS' if v.passed else 'FAIL'}: {ins.get('summary', '')[:100]}")
                for e in v.errors:
                    print(f"   error  : {e}")
                for w in v.warnings:
                    print(f"   warning: {w}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump([{"id": v.insight_id, "kind": v.kind, "passed": v.passed,
                        "errors": v.errors, "warnings": v.warnings} for v in verdicts], fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
