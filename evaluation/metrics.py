"""Ranking metrics for the retrieval evaluation.

Each query has exactly one relevant item, so a query's outcome is fully
described by the 1-based rank at which that item came back (None = not
returned at all). Everything below is computed from that list of ranks.
"""

from typing import Iterable, List, Optional


def recall_at_k(ranks: Iterable[Optional[int]], k: int) -> float:
    """Share of queries whose relevant item is in the top k."""
    ranks = list(ranks)
    if not ranks:
        return 0.0
    return sum(1 for r in ranks if r is not None and r <= k) / len(ranks)


def mean_reciprocal_rank(ranks: Iterable[Optional[int]]) -> float:
    """Mean of 1/rank (0 for a miss). 1.0 = always ranked first."""
    ranks = list(ranks)
    if not ranks:
        return 0.0
    return sum(1.0 / r for r in ranks if r is not None) / len(ranks)


def random_baseline(n_candidates: int, k: int) -> dict:
    """Expected recall@k and MRR if the n candidates were ranked at random
    (the relevant item is equally likely to land at any rank 1..n)."""
    if n_candidates <= 0:
        return {"recall_at_k": 0.0, "mrr": 0.0}
    ranks: List[int] = list(range(1, n_candidates + 1))
    return {
        "recall_at_k": min(k, n_candidates) / n_candidates,
        "mrr": sum(1.0 / r for r in ranks) / n_candidates,
    }
