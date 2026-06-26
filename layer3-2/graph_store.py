"""The knowledge graph itself: a networkx DiGraph, persisted as node-link JSON.

This module is the thin storage seam, exactly analogous to layer3-1/store.py
for vectors. Everything above it (builder, queries) speaks Node/Edge and never
touches networkx directly, so the backend could later be swapped for a real
graph database without changing those files.

Why networkx + a JSON file (rather than a graph DB):
  * the corpus is tiny (ref.md: a focused AI-research subset), so an in-memory
    graph is instant to build and traverse;
  * node-link JSON is the standard, lossless interchange format networkx ships
    with -- human-readable, diffable, and re-loadable without rebuilding;
  * it keeps the dependency footprint to one new package, matching the
    project's "minimal deps" stance.

A DiGraph (directed) is the right model because every edge type has a
direction (Paper -AUTHORED-by? no: Author -AUTHORED-> Paper). We allow at most
one edge of a given (source, target) pair at the networkx level by storing the
edge ``type`` as an attribute; the builder never creates two different typed
edges between the same ordered pair in this schema, so a DiGraph (not a
MultiDiGraph) keeps queries simple.
"""

import os
import json
import logging
from typing import Dict, List, Optional

import networkx as nx
from networkx.readwrite import json_graph

from .config import Config
from .models import Edge, Node

logger = logging.getLogger(__name__)


class GraphStore:
    """Wraps a networkx DiGraph with add/persist/load and small accessors."""

    def __init__(self, graph: Optional[nx.DiGraph] = None):
        # nodes carry: type, label, aliases, plus everything in Node.attrs
        # edges carry: type, plus everything in Edge.attrs
        self.g: nx.DiGraph = graph if graph is not None else nx.DiGraph()

    # --- building ----------------------------------------------------------

    def add_node(self, node: Node) -> None:
        """Insert or update a node, flattening Node.attrs onto the networkx
        node so queries can read them directly as ``g.nodes[id]["year"]`` etc."""
        self.g.add_node(
            node.id,
            type=node.type,
            label=node.label,
            aliases=node.aliases,
            **node.attrs,
        )

    def add_edge(self, edge: Edge) -> None:
        """Insert a typed edge, flattening Edge.attrs the same way."""
        self.g.add_edge(
            edge.source,
            edge.target,
            type=edge.type,
            **edge.attrs,
        )

    def has_node(self, node_id: str) -> bool:
        return self.g.has_node(node_id)

    # --- persistence -------------------------------------------------------

    def save(self, path: str) -> None:
        """Write the graph to ``path`` as node-link JSON.

        We pass edges="links" explicitly: networkx 3.x is mid-migration on the
        default key name, and pinning it keeps the on-disk format stable (and
        silences the FutureWarning) across networkx versions.
        """
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        data = json_graph.node_link_data(self.g, edges="links")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        logger.info("wrote graph to %s (%d nodes, %d edges)",
                    path, self.g.number_of_nodes(), self.g.number_of_edges())

    @classmethod
    def load(cls, path: str) -> "GraphStore":
        """Load a graph previously written by save(); no rebuild needed."""
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{path} not found -- build the graph first with: "
                f"python -m layer3-2 build")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        g = json_graph.node_link_graph(data, directed=True, edges="links")
        logger.info("loaded graph from %s (%d nodes, %d edges)",
                    path, g.number_of_nodes(), g.number_of_edges())
        return cls(g)

    # --- small accessors used by stats/queries -------------------------------

    def nodes_by_type(self) -> Dict[str, List[str]]:
        """Map each node type to the ids of nodes of that type."""
        out: Dict[str, List[str]] = {}
        for node_id, data in self.g.nodes(data=True):
            out.setdefault(data.get("type", "?"), []).append(node_id)
        return out

    def nodes_by_type_counts(self) -> Dict[str, int]:
        """Count nodes per type (stub vs real Paper split out, since citation
        stubs can otherwise dwarf the real graph)."""
        out: Dict[str, int] = {}
        for _, data in self.g.nodes(data=True):
            t = data.get("type", "?")
            if t == "Paper" and data.get("stub"):
                t = "Paper(stub)"
            out[t] = out.get(t, 0) + 1
        return out

    def edges_by_type(self) -> Dict[str, int]:
        """Count edges per edge type."""
        out: Dict[str, int] = {}
        for _, _, data in self.g.edges(data=True):
            t = data.get("type", "?")
            out[t] = out.get(t, 0) + 1
        return out
