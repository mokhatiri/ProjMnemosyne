"""Data model for the embedding & retrieval layer.

Mirrors the style of layer1/models.py and layer2/models.py: plain dataclasses.

The central idea of Layer 3-1 is that everything searchable -- a paper's
abstract, a single claim, a method, a result -- becomes a uniform `Chunk`.
One text, one vector, one metadata bag. Two granularities fall out naturally:

  * kind == "abstract"        -> paper-level search ("find related papers")
  * kind == "claim"/"method"/ -> unit-level search ("find claims about X",
    "dataset"/"result"/...       "which papers use method Y")

because a kind filter at query time selects the granularity.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

# Every chunk kind the indexer produces: the paper-level kind plus one kind
# per Layer 2 unit type. Search filters validate against this.
CHUNK_KINDS = ("abstract", "claim", "method", "dataset", "result",
               "assumption", "limitation")


@dataclass
class Chunk:
    """One embeddable/searchable unit of text.

    ``chunk_id`` is deterministic (e.g. "arxiv:2606.11189v1#claim:0") so that
    re-running the indexer can recognise chunks it has already embedded --
    that is what makes indexing idempotent.

    ``metadata`` carries everything a search filter or a downstream layer
    might want: paper title, categories, published year, and the unit's own
    fields (section, claim_type, confidence, role, metric, ...). Kept as a
    plain dict because the fields differ per kind.
    """
    chunk_id: str
    paper_id: str
    kind: str                       # one of CHUNK_KINDS
    text: str                       # what actually gets embedded
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    """One search result: the chunk plus its cosine similarity to the query
    (1.0 = identical direction, 0 = unrelated, negative = opposed)."""
    chunk: Chunk
    score: float
