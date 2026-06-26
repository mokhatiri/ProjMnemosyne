"""The public retrieval API -- what the rest of the system imports.

Layers 4/5 (knowledge graph, MCP tools, analytical agents) call exactly two
module-level functions:

    search(query, k=10, kind=None, **filters) -> List[SearchHit]
    more_like(paper_id, k=10)                 -> List[SearchHit]

Because the package directory contains a hyphen, `import layer3-1.search` is
a SyntaxError; external callers import it via importlib instead:

    import importlib
    retrieval = importlib.import_module("layer3-1.search")
    hits = retrieval.search("chain of thought prompting", k=5, kind="claim")

The store and the query embedder are lazy module-level singletons: loaded on
first call, reused afterwards. The query embedder is chosen to match *the
store's* recorded model (vectors.meta.json) -- not the configured default --
so queries always land in the same vector space as the index, including when
the index was built with --fake-embeddings.
"""

import logging
from typing import List, Optional

from .config import Config
from .embedder import FakeEmbedder, VoyageEmbedder
from .models import CHUNK_KINDS, SearchHit
from .store import VectorStore

logger = logging.getLogger(__name__)

# lazy singletons (built by _ensure_loaded on first use)
_store: Optional[VectorStore] = None
_embedder = None


def _ensure_loaded(config: Optional[Config] = None) -> None:
    """Load the store once and pick the embedder that matches its meta.

    Builds into locals and assigns the module globals only once *both* the
    store and the embedder are ready. If embedder construction raises (e.g. a
    real store but no VOYAGE_API_KEY -> RuntimeError), the globals stay None so
    the next call retries cleanly and raises the same clear error -- rather than
    leaving _store set with _embedder None, which would surface as an opaque
    AttributeError on the following call.
    """
    global _store, _embedder
    if _store is not None and _embedder is not None:
        return
    config = config or Config()
    store = VectorStore(config)
    if not len(store):
        raise RuntimeError(
            "the vector store is empty -- build it first with: "
            "python -m layer3-1 index")
    model = store.meta["model"]
    if model.startswith("fake-hash-"):
        embedder = FakeEmbedder(config, dim=store.meta["dim"])
    else:
        embedder = VoyageEmbedder(config, model=model)   # may raise before we commit
    _store, _embedder = store, embedder
    logger.info("retrieval ready: %d chunks, querying with %s",
                len(_store), _embedder.model_name)


def reload() -> None:
    """Drop the singletons so the next call re-reads the store from disk
    (use after indexing new papers in the same process)."""
    global _store, _embedder
    _store = None
    _embedder = None


def search(query: str, k: int = 10, kind: Optional[str] = None,
           **filters) -> List[SearchHit]:
    """Semantic search over the corpus.

    ``kind`` selects the granularity: "abstract" for paper-level hits,
    "claim"/"method"/... for unit-level ones, None for everything mixed.
    Extra keyword filters pass through to the store: paper_id=...,
    category="cs.LG", year=2026, claim_type="empirical", ...
    """
    if kind is not None and kind not in CHUNK_KINDS:
        raise ValueError(f"unknown kind {kind!r}; expected one of {CHUNK_KINDS}")
    _ensure_loaded()
    # input_type="query": Voyage embeds queries and documents asymmetrically
    # into the same space (better retrieval than symmetric embedding)
    query_vec = _embedder.embed([query], input_type="query")[0]
    return _store.search(query_vec, k=k, filter={"kind": kind, **filters})


def more_like(paper_id: str, k: int = 10) -> List[SearchHit]:
    """Papers related to a given paper (paper-level similarity).

    Reuses the paper's *stored* abstract vector as the query -- no embedding
    API call -- and excludes the paper itself from the results.
    """
    _ensure_loaded()
    query_vec = _store.vector_for(f"{paper_id}#abstract")
    if query_vec is None:
        raise ValueError(
            f"paper {paper_id!r} has no abstract chunk in the store -- "
            f"is it indexed? (python -m layer3-1 index)")
    return _store.search(query_vec, k=k, filter={"kind": "abstract"},
                         exclude_paper_ids={paper_id})
