"""Layer 3-1: Embedding & Retrieval (ref.md §3.3).

The directory name contains a hyphen, so the *import statement* cannot name
this package (`import layer3-1` is a SyntaxError). Everything inside the
package uses relative imports, the CLI works as `python -m layer3-1`, and
external callers (Layers 4/5) load the public API via importlib:

    import importlib
    retrieval = importlib.import_module("layer3-1.search")
    hits = retrieval.search("contrastive pretraining", k=5, kind="claim")
    related = retrieval.more_like("arxiv:2606.11189v1")
"""

from .config import Config
from .models import CHUNK_KINDS, Chunk, SearchHit
from .embedder import FakeEmbedder, VoyageEmbedder
from .store import VectorStore
from .index import build_chunks, run_index
from .search import more_like, search

__all__ = [
    "Config",
    "CHUNK_KINDS",
    "Chunk",
    "SearchHit",
    "FakeEmbedder",
    "VoyageEmbedder",
    "VectorStore",
    "build_chunks",
    "run_index",
    "search",
    "more_like",
]
