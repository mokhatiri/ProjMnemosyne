""" Has only one model :) """
"""Source-agnostic data model shared by every fetcher and the rest of the pipeline."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Paper:
    """A source-agnostic paper record. Every fetcher maps into this shape so the
    rest of the pipeline (extraction, embedding, graph) never sees source quirks."""
    source: str                      # "arxiv" | "semantic_scholar" | "openreview"
    source_id: str                   # id within that source
    title: str
    abstract: str = ""
    authors: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    published: Optional[str] = None  # ISO date string
    pdf_url: Optional[str] = None    # kept for on-demand re-fetch; PDF itself is discarded
    doi: Optional[str] = None
    references: List[str] = field(default_factory=list)  # source ids / external ids
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def paper_id(self) -> str:
        """Stable global id used as the primary key downstream."""
        return f"{self.source}:{self.source_id}"
