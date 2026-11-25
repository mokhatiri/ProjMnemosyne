"""Insight verification: deterministic checks that a banked insight stands on
the corpus (see checks.py). Used by the analyst as a gate before banking, and
as a report over storage/insights.jsonl (python -m verifier)."""

from .checks import Corpus, Verdict, check, check_all  # noqa: F401
