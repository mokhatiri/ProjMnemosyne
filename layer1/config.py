"""
Configuration file for the paper fetcher module.
"""

import os


class Config:
    """
    Configuration class to hold all the settings for the paper fetcher module.
    """
    def __init__(self):
        # API keys and endpoints
        self.arxiv_api_endpoint = "http://export.arxiv.org/api/query"
        # S2 Graph API (the v1 paper endpoint is legacy; the graph API is the current one).
        self.semantic_scholar_api_endpoint = "https://api.semanticscholar.org/graph/v1"
        # Optional S2 API key: lifts you out of the heavily rate-limited anonymous
        # pool (which often returns 429). Set S2_API_KEY in the environment.
        self.semantic_scholar_api_key = os.environ.get("S2_API_KEY")
        self.openreview_api_endpoint = "https://api.openreview.net"

        # Storage settings
        self.storage_type = "local"
        self.local_storage_path = "./storage"

        # GROBID settings
        self.grobid_endpoint = "http://localhost:8070/api/processFulltextDocument"

        # HTTP behaviour
        self.user_agent = "ProjMnemosyne-paper-fetcher/0.1 (research use)"
        self.request_timeout = 30  # seconds
        self.max_retries = 3