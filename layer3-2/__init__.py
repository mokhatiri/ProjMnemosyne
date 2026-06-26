"""Layer 3-2: Knowledge Graph (ref.md §3.4).

Builds a networkx graph of Papers, Claims, Methods, Datasets, and Authors from
the Layer 1 + Layer 2 JSONL output, and exposes traversal queries for the MCP
tools (Layer 4) and analytical agents (Layer 5).

The directory name contains a hyphen, so `import layer3-2` is a SyntaxError.
Inside the package everything uses relative imports, the CLI runs as
`python -m layer3-2`, and external callers load the query API via importlib:

    import importlib
    kg = importlib.import_module("layer3-2.queries")
    kg.papers_using("TARGET-SFT")
    kg.coverage_gaps()
"""

from .config import Config
from .models import EDGE_TYPES, NODE_TYPES, Edge, Node
from .graph_store import GraphStore
from .builder import BuildReport, build, normalize
from .queries import (
    citation_chain, claims_about, coverage_gaps, load, neighbors,
    papers_using, reload, shared_datasets,
)

__all__ = [
    "Config",
    "Node",
    "Edge",
    "NODE_TYPES",
    "EDGE_TYPES",
    "GraphStore",
    "build",
    "BuildReport",
    "normalize",
    "load",
    "reload",
    "neighbors",
    "papers_using",
    "claims_about",
    "citation_chain",
    "shared_datasets",
    "coverage_gaps",
]
