"""
Configuration for the autonomous analyst.

The analyst is the self-directed driver that runs the Layer 5 agents on a loop,
picks its own targets from the knowledge graph, and accumulates ranked insights
over time -- unattended. These knobs control pace and where it keeps state.
"""

import os


class Config:
    """Settings for the autonomous analysis loop."""

    def __init__(self):
        self.local_storage_path = "./storage"
        self.insights_filename = "insights.jsonl"        # accumulated, ranked findings
        self.state_filename = "analyst_state.json"       # resume ledger (done tasks, iteration)

        # Pace. The analyst is meant to run *slowly* in the background, so the
        # default gap between generations is long. Each generation also only
        # works a small batch of tasks, so the corpus is chewed through
        # gradually rather than hammered.
        self.interval_seconds = int(os.environ.get("ANALYST_INTERVAL", "900"))  # 15 min
        self.batch_size = int(os.environ.get("ANALYST_BATCH", "4"))   # tasks per generation
        self.default_k = 8        # units each agent gathers per probe

    @property
    def insights_path(self) -> str:
        return os.path.join(self.local_storage_path, self.insights_filename)

    @property
    def state_path(self) -> str:
        return os.path.join(self.local_storage_path, self.state_filename)
