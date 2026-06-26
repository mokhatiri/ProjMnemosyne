"""
Configuration for the Layer 5 analytical-agent layer.

Same pattern as the other layers: a plain class whose __init__ sets every knob.

The agents reuse Layer 4's tools (and thus its retrieval/graph/LLM wiring); the
only extra LLM work Layer 5 owns is synergy detection and evidence aggregation,
which run through a Reasoner that *subclasses* Layer 4's (reasoner.py) -- so the
HF-call settings here mirror Layer 4's.
"""

import os


class Config:
    """All settings for the analytical-agent layer."""

    def __init__(self):
        # --- output (append-only, like every other layer's sink) --------------
        self.local_storage_path = "./storage"
        self.findings_filename = "findings.jsonl"   # one Finding per line

        # --- LLM for synergy / evidence reasoning -----------------------------
        # Same Hugging Face Inference defaults as Layers 2 and 4 so the project
        # speaks to one provider. These attribute names match what Layer 4's
        # HFReasoner.__init__ reads (model / hf_provider / max_output_tokens /
        # max_api_retries), which is what lets reasoner.py subclass it cleanly.
        self.model = os.environ.get(
            "LAYER5_MODEL",
            os.environ.get("LAYER4_MODEL", "Qwen/Qwen2.5-72B-Instruct"))
        self.hf_provider = os.environ.get("LAYER5_HF_PROVIDER", "auto")
        self.max_output_tokens = 4096
        self.max_api_retries = 3

        # --- agent defaults -----------------------------------------------------
        self.default_k = 8        # how many units an agent gathers per probe

    @property
    def findings_path(self) -> str:
        return os.path.join(self.local_storage_path, self.findings_filename)
