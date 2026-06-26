"""Node/Edge data model for the knowledge graph (ref.md §3.4).

Mirrors the house style of layer1/models.py .. layer3-1/models.py: plain
dataclasses, no framework.

Everything the graph stores is one of two shapes:

  * Node -- a Paper, Claim, Method, Dataset, or Author.
  * Edge -- a typed, directed relationship between two nodes.

The single most important design choice here is that **ids are deterministic
and content-derived**, never random:

    paper:<paper_id>            paper:arxiv:2606.11189v1
    author:<norm>              author:jason wei
    method:<norm>              method:chain of thought prompting
    dataset:<norm>            dataset:gsm8k
    claim:<paper_id>:<i>       claim:arxiv:2606.11189v1:0

Why it matters: builder.py rebuilds the whole graph from scratch on every run
(the graph is fully derived data). Deterministic ids mean two runs over the
same input produce byte-identical node sets, and -- crucially for entity
resolution -- two different spellings of "BERT" normalize to the *same*
method id and therefore collapse into one node automatically, before any
semantic step even runs.

`Node.aliases` records every surface spelling that collapsed into the node, so
a human can audit (and undo) a bad merge later.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

# Every node/edge label the builder emits. Queries and stats validate against
# these so a typo'd edge_type fails loudly instead of silently matching nothing.
NODE_TYPES = ("Paper", "Claim", "Method", "Dataset", "Author")
EDGE_TYPES = (
    "MAKES_CLAIM",   # Paper  -> Claim
    "INTRODUCES",    # Paper  -> Method   (role == "introduced")
    "USES",          # Paper  -> Method   (role == "used")
    "EVALUATES_ON",  # Paper  -> Dataset  (carries metric/value when known)
    "CITES",         # Paper  -> Paper    (may point at a stub paper)
    "AUTHORED",      # Author -> Paper
    "ABOUT",         # Claim  -> Method | Dataset
)


@dataclass
class Node:
    """One vertex in the knowledge graph.

    ``attrs`` holds type-specific fields (a Paper's title/year, a Claim's
    claim_type/confidence/section, a Method's role, ...) so the dataclass
    stays uniform while carrying arbitrary payloads into networkx.
    """
    id: str
    type: str                                   # one of NODE_TYPES
    label: str                                  # human-readable name/snippet
    aliases: List[str] = field(default_factory=list)   # merged surface spellings
    attrs: Dict[str, Any] = field(default_factory=dict)

    def add_alias(self, spelling: str) -> None:
        """Record a surface spelling that resolved to this node (deduped,
        order-preserving). The canonical ``label`` counts as an alias too, so
        we never store it twice."""
        if spelling and spelling != self.label and spelling not in self.aliases:
            self.aliases.append(spelling)


@dataclass
class Edge:
    """One directed, typed relationship ``source -> target``.

    ``attrs`` carries edge payloads -- most importantly the metric/value an
    EVALUATES_ON edge picks up when a dataset name matches a reported result.
    """
    source: str                                 # source node id
    target: str                                 # target node id
    type: str                                   # one of EDGE_TYPES
    attrs: Dict[str, Any] = field(default_factory=dict)
