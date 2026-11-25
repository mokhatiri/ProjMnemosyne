"""Offline retrieval evaluation over the Layer 3-1 vector store.

Task: "unit -> source paper" (known-item retrieval).
Every extracted unit (claim, method, result, dataset, assumption, limitation)
comes from exactly one paper. We use the unit's *stored* embedding as the
query, search the paper-level index (kind="abstract") through the store's own
search(), and record the rank at which the unit's source paper comes back.
Recall@k and MRR follow from those ranks.

Why this task: it needs no hand labels (the extraction already records each
unit's paper), no API calls (vectors are on disk) and it is deterministic, so
anyone can re-run it and get the same numbers. It measures whether the
embedding space keeps a paper's units closer to that paper than to the
others -- the property `search(..., kind="abstract")` relies on.

Limits, stated with every report: the candidate pool is only the papers that
are indexed (11 in the June 2026 run), queries reuse document-side
embeddings (search() embeds live queries with input_type="query" instead),
and a random ranking already scores recall@5 = 5/N; the baseline is printed
next to the result so the number is never read without it.
"""

import importlib
from collections import defaultdict
from typing import Dict, List, Optional

from .metrics import mean_reciprocal_rank, random_baseline, recall_at_k

_l31_config = importlib.import_module("layer3-1.config")
_l31_store = importlib.import_module("layer3-1.store")


def rank_source_papers(store) -> List[dict]:
    """One record per unit chunk: its kind, paper and the rank of its paper."""
    abstracts = [c for c in store.chunks if c.kind == "abstract"]
    n_papers = len(abstracts)
    indexed_papers = {c.paper_id for c in abstracts}
    records = []
    for i, chunk in enumerate(store.chunks):
        if chunk.kind == "abstract" or chunk.paper_id not in indexed_papers:
            continue
        hits = store.search(store.vectors[i], k=n_papers,
                            filter={"kind": "abstract"})
        rank: Optional[int] = None
        for pos, hit in enumerate(hits, start=1):
            if hit.chunk.paper_id == chunk.paper_id:
                rank = pos
                break
        records.append({"chunk_id": chunk.chunk_id, "kind": chunk.kind,
                        "paper_id": chunk.paper_id, "rank": rank})
    return records


def summarise(records: List[dict], n_papers: int, k: int = 5) -> Dict:
    ranks = [r["rank"] for r in records]
    by_kind = defaultdict(list)
    for r in records:
        by_kind[r["kind"]].append(r["rank"])
    return {
        "task": "unit -> source paper (known-item, stored vectors)",
        "queries": len(records),
        "candidates": n_papers,
        f"recall@1": recall_at_k(ranks, 1),
        f"recall@{k}": recall_at_k(ranks, k),
        "mrr": mean_reciprocal_rank(ranks),
        "random_baseline": random_baseline(n_papers, k),
        "by_kind": {
            kind: {"queries": len(rs), f"recall@{k}": recall_at_k(rs, k),
                   "mrr": mean_reciprocal_rank(rs)}
            for kind, rs in sorted(by_kind.items())
        },
    }


def run(storage_path: Optional[str] = None, k: int = 5) -> Dict:
    config = _l31_config.Config()
    if storage_path:
        config.local_storage_path = storage_path
    store = _l31_store.VectorStore(config)
    if not len(store):
        raise RuntimeError("the vector store is empty -- build it first with: "
                           "python -m layer3-1 index")
    n_papers = sum(1 for c in store.chunks if c.kind == "abstract")
    result = summarise(rank_source_papers(store), n_papers, k)
    result["model"] = (store.meta or {}).get("model")
    return result
