"""
Configuration for the top-level pipeline orchestrator.

Plain-class pattern like the other layers. The orchestrator owns no data of its
own -- it drives the per-layer CLIs and then launches the frontend -- so these
are just the run defaults.
"""


class Config:
    """Defaults for a full-pipeline run."""

    def __init__(self):
        # Layer 1 ingestion (only runs when --ingest N > 0, since it needs the
        # network and optionally GROBID).
        self.default_sources = ["arxiv"]
        self.default_limit = 5

        # Frontend console.
        self.host = "127.0.0.1"
        self.port = 8000
