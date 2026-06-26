"""ProjMnemosyne pipeline orchestrator.

One entry point that runs every layer end-to-end (Layer 1 ingest -> Layer 2
extract -> Layer 3-1 index -> Layer 3-2 graph -> optional Layer 6 A2A report)
and then launches the frontend console (Layers 4-6).

    python -m pipeline                 # build the stack, then serve the UI
    python -m pipeline --no-serve      # build only

See runner.run_pipeline for the programmatic entry point.
"""

from .config import Config
from .runner import run_pipeline

__all__ = ["Config", "run_pipeline"]
