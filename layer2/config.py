"""
Configuration for the Layer 2 knowledge-extraction module.

Extends the Layer 1 pattern (layer1/config.py): a plain class whose __init__
sets every knob, reading the environment where it makes sense. No framework.
"""

import os


class Config:
    """All settings for the knowledge-extraction pipeline."""

    def __init__(self):
        # --- Hugging Face Inference API ---------------------------------------
        # Extraction runs on an open model served through HF inference
        # providers. The default is a strong, ungated instruct model that is
        # good at structured JSON; override per-run with the LAYER2_MODEL env
        # var or the --model CLI flag.
        self.model = os.environ.get("LAYER2_MODEL", "Qwen/Qwen2.5-72B-Instruct")
        # Which inference provider to route through. "auto" lets Hugging Face
        # pick the first provider currently serving the model; pin a specific
        # one (e.g. "together", "nebius") when reproducibility matters.
        self.hf_provider = os.environ.get("LAYER2_HF_PROVIDER", "auto")
        # Cap on the *response* size. Extraction output for one paper is a few
        # KB of JSON; some providers reject very large max_tokens values, so
        # keep this modest rather than maximal.
        self.max_output_tokens = 8192

        # --- chunking ---------------------------------------------------------
        # Approximate input-token budget for the paper text in one API call.
        # Papers longer than this are split into section groups, extracted per
        # group, and the units merged. Token counts are estimated at ~4 chars
        # per token (close enough for budgeting; we never need exact counts).
        self.max_chunk_tokens = 30000

        # --- retries ----------------------------------------------------------
        # API-level retries on 429/5xx, with exponential backoff (mirrors the
        # retry loop in layer1/base_fetcher._get). The SDK's own auto-retry is
        # disabled so this is the single retry layer (easier to reason about).
        self.max_api_retries = 3
        # Validation-level retries: if the model returns JSON that fails our
        # dataclass validation, re-ask once with the error message included.
        self.max_validation_retries = 1

        # --- storage (same layout/conventions as Layer 1) ----------------------
        self.local_storage_path = "./storage"
        self.metadata_filename = "metadata.jsonl"    # input, written by Layer 1
        self.extracted_filename = "extracted.jsonl"  # output, append-only JSONL

        # --- concurrency --------------------------------------------------------
        # Papers are independent, so they extract in parallel (I/O bound on the
        # API). Kept low by default to stay friendly to rate limits.
        self.max_workers = 2

    # convenience paths, so callers never re-join these themselves
    @property
    def metadata_path(self) -> str:
        return os.path.join(self.local_storage_path, self.metadata_filename)

    @property
    def extracted_path(self) -> str:
        return os.path.join(self.local_storage_path, self.extracted_filename)
