"""
Configuration for the Layer 3-2 knowledge-graph module.

Same pattern as layer1/config.py .. layer3-1/config.py: a plain class whose
__init__ sets every knob. No framework.

Note: this layer is intentionally self-contained. Entity resolution is
normalization + a small alias table (see builder.py) -- it does NOT consult
Layer 3-1's vector store, so there are no embedding/model knobs here. ref.md
treats Embedding/Retrieval (3-1) and Knowledge Graph (3-2) as parallel layers,
and keeping them decoupled means a graph build never depends on 3-1's state.
"""

import os


class Config:
    """All settings for the knowledge-graph build & query pipeline."""

    def __init__(self):
        # --- storage (shared with every other layer) --------------------------
        self.local_storage_path = "./storage"
        self.metadata_filename = "metadata.jsonl"     # input, from Layer 1
        self.extracted_filename = "extracted.jsonl"   # input, from Layer 2
        self.graph_filename = "graph.json"            # output: node-link graph

    # convenience paths, so callers never re-join these themselves
    @property
    def metadata_path(self) -> str:
        return os.path.join(self.local_storage_path, self.metadata_filename)

    @property
    def extracted_path(self) -> str:
        return os.path.join(self.local_storage_path, self.extracted_filename)

    @property
    def graph_path(self) -> str:
        return os.path.join(self.local_storage_path, self.graph_filename)
