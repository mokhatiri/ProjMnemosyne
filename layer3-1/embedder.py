"""Text -> vector, via the Voyage AI embeddings API (or a deterministic fake).

Two embedders share one tiny interface -- ``embed(texts, input_type)`` returns
an (n, dim) float32 numpy array, and ``model_name`` identifies the vector
space -- so the indexer and the search layer never care which one they hold:

  * VoyageEmbedder -- the real thing. Called with `requests` exactly like
    Layer 1 talks to arXiv/S2 (no SDK, no torch), with the same hand-rolled
    429/5xx retry/backoff pattern as layer1/base_fetcher._get.
  * FakeEmbedder -- offline mode for --fake-embeddings: vectors derived from
    a hash of the text. Deterministic (same text -> same vector, across runs
    and machines), so chunking/store/idempotency logic can be exercised
    without an API key. Semantically meaningless: only *identical* texts
    score ~1.0; everything else is noise.

`input_type` matters for Voyage: documents are embedded with
input_type="document" at index time and queries with input_type="query" at
search time -- the model embeds them into the same space but optimises each
side for retrieval. The fake embedder ignores it (hashing has no sides).
"""

import os
import time
import hashlib
import logging
from typing import List

import numpy as np
import requests

from .config import Config

logger = logging.getLogger(__name__)


class VoyageEmbedder:
    """Embeddings via POST https://api.voyageai.com/v1/embeddings."""

    def __init__(self, config: Config, model: str = None):
        self.config = config
        # the store can demand a specific model (the one it was built with),
        # which overrides the configured default
        self.model_name = model or config.model
        api_key = os.environ.get("VOYAGE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "VOYAGE_API_KEY is not set. Layer 3-1 calls the Voyage AI API "
                "for embeddings; create a key at https://dashboard.voyageai.com "
                "and export it first, e.g.\n"
                "  PowerShell: $env:VOYAGE_API_KEY = 'pa-...'\n"
                "  bash:       export VOYAGE_API_KEY='pa-...'\n"
                "(or run indexing with --fake-embeddings to test the pipeline "
                "without a key)")
        self.session = requests.Session()   # connection reuse across batches
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def embed(self, texts: List[str], input_type: str = "document") -> np.ndarray:
        """Embed any number of texts, batching at the API's 128-text limit."""
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        vectors: List[List[float]] = []
        for start in range(0, len(texts), self.config.batch_size):
            batch = texts[start:start + self.config.batch_size]
            logger.info("embedding batch %d-%d of %d (%s)",
                        start + 1, start + len(batch), len(texts), self.model_name)
            vectors.extend(self._embed_batch(batch, input_type))
        return np.asarray(vectors, dtype=np.float32)

    def _embed_batch(self, batch: List[str], input_type: str) -> List[List[float]]:
        """One API call with 429/5xx retry/backoff (the Layer 1 pattern)."""
        payload = {"input": batch, "model": self.model_name,
                   "input_type": input_type}
        last_exc = None
        for attempt in range(1, self.config.max_api_retries + 1):
            try:
                resp = self.session.post(self.config.voyage_api_endpoint,
                                         json=payload,
                                         timeout=self.config.request_timeout)
            except requests.RequestException as exc:
                wait = 2 ** attempt
                logger.warning("embedding request failed (attempt %d/%d): %s",
                               attempt, self.config.max_api_retries, exc)
                last_exc = exc
                time.sleep(wait)
                continue

            if resp.status_code == 429 or resp.status_code >= 500:
                # honour the server's Retry-After when present, else back off
                retry_after = resp.headers.get("Retry-After", "")
                wait = int(retry_after) if retry_after.isdigit() else 2 ** attempt
                logger.warning("embeddings API -> %d (attempt %d/%d), backing off %ds",
                               resp.status_code, attempt,
                               self.config.max_api_retries, wait)
                last_exc = RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(wait)
                continue

            if not resp.ok:   # other 4xx (bad key, bad model) won't heal
                raise RuntimeError(
                    f"embeddings API rejected the request "
                    f"({resp.status_code}): {resp.text[:300]}")

            data = resp.json()["data"]
            # the API documents order-preservation, but it also tags each
            # vector with its input index -- sort on it to be safe
            data.sort(key=lambda item: item["index"])
            return [item["embedding"] for item in data]

        raise last_exc   # exhausted retries


class FakeEmbedder:
    """Deterministic hash-based vectors for offline testing (--fake-embeddings).

    The text's SHA-256 seeds numpy's RNG, which then draws a Gaussian vector;
    Gaussian draws spread direction uniformly on the sphere, so unrelated
    texts land near-orthogonal (score ~0) and identical texts collide exactly
    (score 1.0). Good enough to prove the plumbing; useless for semantics.
    """

    def __init__(self, config: Config, dim: int = None):
        self.dim = dim or config.fake_dim
        # the dimension is part of the vector space's identity, so it is
        # baked into the model name the store records
        self.model_name = f"fake-hash-{self.dim}"

    def embed(self, texts: List[str], input_type: str = "document") -> np.ndarray:
        del input_type   # hashing has no document/query distinction
        vectors = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            seed = int.from_bytes(
                hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
            vectors[i] = np.random.default_rng(seed).standard_normal(self.dim)
        return vectors
