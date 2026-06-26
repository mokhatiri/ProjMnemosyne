"""Concrete paper-source fetchers, one module per source."""

from .arxiv import ArxivFetcher
from .semantic_scholar import SemanticScholarFetcher
from .openreview import OpenReviewFetcher

__all__ = ["ArxivFetcher", "SemanticScholarFetcher", "OpenReviewFetcher"]
