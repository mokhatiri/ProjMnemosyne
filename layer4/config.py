"""
Configuration for the Layer 4 MCP tool layer.

Same pattern as the other layers (layer1/config.py ..): a plain class whose
__init__ sets every knob, reading the environment where it makes sense.

Layer 4 exposes structured tools to an LLM/agent over the Model Context
Protocol. Three kinds of knob live here:
  * where the corpus lives (for the keyword fallback that reads the JSONL
    files directly when the Layer 3-1 vector store can't be queried),
  * the LLM used by the two *reasoning* tools (detect_contradictions /
    generate_hypotheses) -- the same Hugging Face Inference setup Layer 2 uses,
    so the project has one LLM provider, and
  * identity for the MCP server itself.
"""

import os


class Config:
    """All settings for the MCP tool layer."""

    def __init__(self):
        # --- corpus (read directly only by the keyword fallback) --------------
        self.local_storage_path = "./storage"
        self.metadata_filename = "metadata.jsonl"     # Layer 1 output
        self.extracted_filename = "extracted.jsonl"   # Layer 2 output

        # --- LLM for the reasoning tools (mirrors layer2/config.py) ------------
        # Hugging Face Inference API: same provider/model defaults as Layer 2 so
        # the whole project speaks to one LLM. Override with LAYER4_MODEL.
        self.model = os.environ.get("LAYER4_MODEL", "Qwen/Qwen2.5-72B-Instruct")
        self.hf_provider = os.environ.get("LAYER4_HF_PROVIDER", "auto")
        self.max_output_tokens = 4096
        self.request_timeout = 60           # seconds
        self.max_api_retries = 3            # 429/5xx retries with backoff

        # --- tool defaults ------------------------------------------------------
        self.default_k = 10                 # default result count for search tools
        # how many candidate units a reasoning tool gathers before asking the LLM
        self.reasoning_candidates = 8

        # --- MCP server identity ------------------------------------------------
        self.server_name = "ProjMnemosyne-research-intelligence"
        self.server_version = "0.1.0"

    @property
    def metadata_path(self) -> str:
        return os.path.join(self.local_storage_path, self.metadata_filename)

    @property
    def extracted_path(self) -> str:
        return os.path.join(self.local_storage_path, self.extracted_filename)
