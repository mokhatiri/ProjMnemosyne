"""Local vector store: numpy matrix + row-aligned JSONL, no external DB.

Layout on disk (all under storage/, next to the other layers' files):

    vectors.npy        (N, dim) float32 -- L2-normalised embedding per row
    chunks.jsonl       N lines -- chunk text + metadata; line i <-> row i
    vectors.meta.json  {"model": ..., "dim": ...} -- which vector space this is

Search is brute-force cosine similarity: vectors are normalised once at add
time, the query once at search time, so cosine reduces to a single matrix-
vector product (`vectors @ query`). At this corpus size (<1M chunks) that is
milliseconds -- the entire point of isolating it behind VectorStore.search()
is that swapping in FAISS / a real vector DB later only touches this file.

The meta file guards against the classic silent failure of vector stores:
querying one model's vectors with another model's query embedding (or mixing
--fake-embeddings runs with real ones). Different spaces -> garbage scores,
no error. We refuse to mix instead.
"""

import os
import json
import logging
from dataclasses import asdict
from typing import Dict, Iterable, List, Optional, Set

import numpy as np

from .config import Config
from .models import Chunk, SearchHit

logger = logging.getLogger(__name__)


def _normalize(matrix: np.ndarray) -> np.ndarray:
    """L2-normalise each row, leaving all-zero rows alone (instead of 0/0)."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (matrix / norms).astype(np.float32)


class VectorStore:
    """The chunks + vectors that have been indexed so far, queryable."""

    def __init__(self, config: Config):
        self.config = config
        self.chunks: List[Chunk] = []
        self.vectors: Optional[np.ndarray] = None     # (N, dim) or None when empty
        self.meta: Optional[dict] = None              # {"model", "dim"} or None
        self.ids: Set[str] = set()                    # chunk_ids, for idempotency
        self._load()

    # --- loading -------------------------------------------------------------

    def _load(self) -> None:
        """Load the three files; tolerate a store that doesn't exist yet."""
        if not os.path.exists(self.config.chunks_path):
            logger.info("no existing vector store at %s (fresh start)",
                        self.config.chunks_path)
            return
        with open(self.config.chunks_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    self.chunks.append(Chunk(**json.loads(line)))
        if os.path.exists(self.config.vectors_path):
            self.vectors = np.load(self.config.vectors_path)
        if os.path.exists(self.config.meta_path):
            with open(self.config.meta_path, encoding="utf-8") as fh:
                self.meta = json.load(fh)

        # Row-alignment is the store's one invariant: line i of chunks.jsonl
        # describes row i of vectors.npy. If the files disagree (e.g. a crash
        # between the two writes), searching would return the wrong chunks for
        # the scores -- refuse loudly instead of corrupting results quietly.
        rows = 0 if self.vectors is None else self.vectors.shape[0]
        if rows != len(self.chunks):
            raise RuntimeError(
                f"vector store is corrupt: {len(self.chunks)} chunks in "
                f"{self.config.chunks_path} but {rows} vectors in "
                f"{self.config.vectors_path}. Delete "
                f"{self.config.vectors_path}, {self.config.chunks_path} and "
                f"{self.config.meta_path}, then re-run indexing.")
        self.ids = {c.chunk_id for c in self.chunks}
        logger.info("loaded vector store: %d chunks (%s)",
                    len(self.chunks), (self.meta or {}).get("model", "no meta"))

    def __len__(self) -> int:
        return len(self.chunks)

    # --- writing ------------------------------------------------------------

    def add(self, chunks: List[Chunk], vectors: np.ndarray, model_name: str) -> None:
        """Append new chunks + their vectors and persist everything."""
        if len(chunks) != vectors.shape[0]:
            raise ValueError(f"{len(chunks)} chunks but {vectors.shape[0]} vectors")
        if not chunks:
            return

        # refuse to mix vector spaces (see module docstring)
        dim = int(vectors.shape[1])
        if self.meta and (self.meta["model"] != model_name or self.meta["dim"] != dim):
            raise RuntimeError(
                f"store was built with model={self.meta['model']} "
                f"(dim={self.meta['dim']}) but you are adding "
                f"model={model_name} (dim={dim}). Mixing vector spaces makes "
                f"scores meaningless. Delete {self.config.vectors_path}, "
                f"{self.config.chunks_path} and {self.config.meta_path} to "
                f"rebuild with the new model.")

        vectors = _normalize(vectors)   # normalise once here, never again
        self.vectors = (vectors if self.vectors is None
                        else np.vstack([self.vectors, vectors]))
        self.chunks.extend(chunks)
        self.ids.update(c.chunk_id for c in chunks)
        self.meta = {"model": model_name, "dim": dim}

        # persist: append-only JSONL for chunks (the Layer 1/2 pattern); the
        # numpy matrix is small enough to just rewrite whole
        os.makedirs(self.config.local_storage_path, exist_ok=True)
        with open(self.config.chunks_path, "a", encoding="utf-8") as fh:
            for chunk in chunks:
                fh.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
        np.save(self.config.vectors_path, self.vectors)
        with open(self.config.meta_path, "w", encoding="utf-8") as fh:
            json.dump(self.meta, fh)
        logger.info("stored %d new chunks (total %d)", len(chunks), len(self.chunks))

    # --- querying ---------------------------------------------------------------

    def vector_for(self, chunk_id: str) -> Optional[np.ndarray]:
        """The stored (normalised) vector of one chunk -- lets more_like()
        reuse an indexed embedding instead of re-calling the API."""
        for i, chunk in enumerate(self.chunks):
            if chunk.chunk_id == chunk_id:
                return self.vectors[i]
        return None

    def _matches(self, chunk: Chunk, filters: Dict) -> bool:
        """Does one chunk pass every metadata filter?

        Recognised keys: kind (str or list of str), paper_id, category
        (membership in the chunk's categories list), year (published year).
        Any other key falls through to plain equality against the metadata
        dict, so future fields are filterable without touching this code.
        """
        for key, want in filters.items():
            if want is None:        # "no constraint" -- lets callers pass kind=None
                continue
            if key == "kind":
                allowed = [want] if isinstance(want, str) else want
                if chunk.kind not in allowed:
                    return False
            elif key == "paper_id":
                if chunk.paper_id != want:
                    return False
            elif key == "category":
                if want not in (chunk.metadata.get("categories") or []):
                    return False
            elif key == "year":
                if chunk.metadata.get("year") != int(want):
                    return False
            elif chunk.metadata.get(key) != want:
                return False
        return True

    def search(self, query_vec: np.ndarray, k: int = 10,
               filter: Optional[Dict] = None,
               exclude_paper_ids: Optional[Iterable[str]] = None) -> List[SearchHit]:
        """Top-k chunks by cosine similarity, honouring metadata filters.

        This signature is the seam for a future FAISS/DB backend: callers know
        nothing about numpy internals, only (vector, k, filters) -> hits.
        """
        if not self.chunks:
            return []

        query = query_vec.astype(np.float32).ravel()
        norm = np.linalg.norm(query)
        if norm == 0:
            return []
        query /= norm

        # one matvec: rows are normalised, query is normalised => cosine
        scores = self.vectors @ query

        # mask out everything the filters reject (score -> -inf so it can
        # never reach the top-k)
        excluded = set(exclude_paper_ids or [])
        if filter or excluded:
            mask = np.fromiter(
                (self._matches(c, filter or {}) and c.paper_id not in excluded
                 for c in self.chunks),
                dtype=bool, count=len(self.chunks))
            scores = np.where(mask, scores, -np.inf)

        # argpartition is O(N) to find the top-k, then we sort just those k
        k = min(k, len(self.chunks))
        top = np.argpartition(-scores, k - 1)[:k]
        top = top[np.argsort(-scores[top])]
        return [SearchHit(chunk=self.chunks[i], score=float(scores[i]))
                for i in top if scores[i] != -np.inf]
