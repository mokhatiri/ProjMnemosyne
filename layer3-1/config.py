"""
Configuration for the Layer 3-1 embedding & retrieval module.

Same pattern as layer1/config.py and layer2/config.py: a plain class whose
__init__ sets every knob, reading the environment where it makes sense.
"""

import os


class Config:
    """All settings for the embedding & retrieval pipeline."""

    def __init__(self):
        # --- Voyage AI embeddings API -----------------------------------------
        # Voyage is called directly with `requests` (like Layer 1 talks to
        # arXiv/S2) -- no torch / sentence-transformers, which keeps the
        # dependency footprint tiny and works on Python 3.14.
        self.voyage_api_endpoint = "https://api.voyageai.com/v1/embeddings"
        # voyage-3: good quality/price for semantic search. Override per-run
        # with the LAYER31_MODEL env var.
        self.model = os.environ.get("LAYER31_MODEL", "voyage-3")
        # Voyage accepts up to 128 texts per request; we always send full
        # batches to minimise round-trips.
        self.batch_size = 128
        self.request_timeout = 60   # seconds; embedding calls can be slow-ish
        self.max_api_retries = 3    # 429/5xx retries with exponential backoff

        # --- fake embeddings (offline mode) -------------------------------------
        # Dimension of the deterministic hash-based vectors used by
        # --fake-embeddings (pipeline testing without an API key). Real
        # voyage-3 vectors are 1024-d; fake ones can be smaller/cheaper.
        self.fake_dim = 256

        # --- storage (same layout/conventions as Layers 1 and 2) ----------------
        self.local_storage_path = "./storage"
        self.metadata_filename = "metadata.jsonl"     # input, from Layer 1
        self.extracted_filename = "extracted.jsonl"   # input, from Layer 2
        self.vectors_filename = "vectors.npy"         # output: the vectors
        self.chunks_filename = "chunks.jsonl"         # output: row-aligned chunk text+metadata
        self.meta_filename = "vectors.meta.json"      # output: which model/dim built the store

    # convenience paths, so callers never re-join these themselves
    @property
    def metadata_path(self) -> str:
        return os.path.join(self.local_storage_path, self.metadata_filename)

    @property
    def extracted_path(self) -> str:
        return os.path.join(self.local_storage_path, self.extracted_filename)

    @property
    def vectors_path(self) -> str:
        return os.path.join(self.local_storage_path, self.vectors_filename)

    @property
    def chunks_path(self) -> str:
        return os.path.join(self.local_storage_path, self.chunks_filename)

    @property
    def meta_path(self) -> str:
        return os.path.join(self.local_storage_path, self.meta_filename)
