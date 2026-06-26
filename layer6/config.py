"""
Configuration for the Layer 6 A2A (agent-to-agent) coordination layer.

Same plain-class pattern as the other layers. Layer 6 owns no LLM of its own --
it orchestrates the Layer 5 agents and cross-validates their structured
findings -- so the only settings here are where to read/write.
"""

import os


class Config:
    """All settings for the coordination layer."""

    def __init__(self):
        self.local_storage_path = "./storage"
        self.reports_filename = "reports.jsonl"   # one consolidated Report per line

    @property
    def reports_path(self) -> str:
        return os.path.join(self.local_storage_path, self.reports_filename)
