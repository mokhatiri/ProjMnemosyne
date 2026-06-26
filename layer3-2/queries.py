"""Public graph-query API -- what Layers 4/5 (MCP tools, agents) call.

Plain module-level functions over the loaded graph, returning plain Python
(dicts/lists of primitives) so the results drop straight into JSON tool
responses. No networkx objects leak across this boundary.

The graph is a lazy module-level singleton (loaded from storage/graph.json on
first use, reused after), the same pattern as layer3-1/search.py. Call
``reload()`` after a rebuild in the same process.

Entity arguments accept either a node id ("method:target sft") or a surface
name ("TARGET-SFT", "the TARGET-SFT method") -- names are run through the same
normalization the builder used, so callers don't need to know node-id syntax.
"""

import logging
from collections import deque
from typing import Any, Dict, List, Optional

from .config import Config
from .builder import normalize
from .graph_store import GraphStore

logger = logging.getLogger(__name__)

# lazy singleton
_store: Optional[GraphStore] = None


def load(config: Optional[Config] = None) -> GraphStore:
    """Load the persisted graph once and cache it."""
    global _store
    if _store is None:
        _store = GraphStore.load((config or Config()).graph_path)
    return _store


def reload() -> None:
    """Drop the cached graph so the next call re-reads it from disk."""
    global _store
    _store = None


# ---------------------------------------------------------------------------
# entity-argument resolution
# ---------------------------------------------------------------------------

def _resolve(name: str, prefer_type: Optional[str] = None) -> Optional[str]:
    """Map a node id OR a surface name to a node id present in the graph.

    Two id conventions coexist: Paper ids embed the *raw* paper_id
    (``paper:semantic_scholar:1b6e8...``), while Method/Dataset/Author ids embed
    the *normalized* name (``method:target sft``). So for each candidate type we
    try both the raw and the normalized form.
    """
    g = load().g
    if g.has_node(name):                       # already a full node id
        return name
    prefixes = ([prefer_type.lower()] if prefer_type
                else ["method", "dataset", "paper", "author"])
    norm = normalize(name)
    for prefix in prefixes:
        for candidate in (f"{prefix}:{name}", f"{prefix}:{norm}"):
            if g.has_node(candidate):
                return candidate
    return _scan_by_label(g, name, prefer_type)   # last resort: label/alias match


def _scan_by_label(g, name: str, prefer_type: Optional[str]) -> Optional[str]:
    """Linear scan for a node whose label or aliases equal ``name`` (covers
    spellings that don't normalize to a known id)."""
    for nid, data in g.nodes(data=True):
        if prefer_type and data.get("type") != prefer_type:
            continue
        if data.get("label") == name or name in (data.get("aliases") or []):
            return nid
    return None


def _node_brief(node_id: str) -> Dict[str, Any]:
    """Compact, JSON-friendly view of a node."""
    data = load().g.nodes[node_id]
    return {"id": node_id, "type": data.get("type"), "label": data.get("label")}


# ---------------------------------------------------------------------------
# public queries
# ---------------------------------------------------------------------------

def neighbors(node_id: str, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Direct neighbours of a node (following out- and in-edges).

    Returns dicts {id, type, label, edge_type, direction, attrs}. ``edge_type``
    filters to one relation; None returns all. ``node_id`` may be a surface
    name -- it's resolved first.
    """
    g = load().g
    resolved = _resolve(node_id)
    if resolved is None:
        logger.warning("neighbors: node %r not found", node_id)
        return []
    out: List[Dict[str, Any]] = []
    for _, tgt, data in g.out_edges(resolved, data=True):
        if edge_type is None or data.get("type") == edge_type:
            out.append({**_node_brief(tgt), "edge_type": data.get("type"),
                        "direction": "out",
                        "attrs": {k: v for k, v in data.items() if k != "type"}})
    for src, _, data in g.in_edges(resolved, data=True):
        if edge_type is None or data.get("type") == edge_type:
            out.append({**_node_brief(src), "edge_type": data.get("type"),
                        "direction": "in",
                        "attrs": {k: v for k, v in data.items() if k != "type"}})
    return out


def papers_using(method: str) -> List[Dict[str, Any]]:
    """Papers that INTRODUCE or USE a method (id or surface name)."""
    g = load().g
    mid = _resolve(method, prefer_type="Method")
    if mid is None:
        logger.warning("papers_using: method %r not found", method)
        return []
    out: List[Dict[str, Any]] = []
    for src, _, data in g.in_edges(mid, data=True):
        if data.get("type") in ("INTRODUCES", "USES"):
            out.append({**_node_brief(src), "relation": data.get("type")})
    return out


def claims_about(entity: str) -> List[Dict[str, Any]]:
    """Claims linked by ABOUT to a method or dataset (id or surface name)."""
    g = load().g
    eid = _resolve(entity)
    if eid is None:
        logger.warning("claims_about: entity %r not found", entity)
        return []
    out: List[Dict[str, Any]] = []
    for src, _, data in g.in_edges(eid, data=True):
        if data.get("type") == "ABOUT":
            node = g.nodes[src]
            out.append({"id": src, "paper_id": node.get("paper_id"),
                        "claim_type": node.get("claim_type"),
                        "statement": node.get("label")})
    return out


def citation_chain(paper_id: str, depth: int = 2) -> Dict[str, Any]:
    """Outgoing CITES tree from a paper, breadth-first up to ``depth`` hops.

    Returns {root, depth, edges:[{from,to,to_label,stub,hop}]}. Stub targets
    (cited papers not in the corpus) are flagged so callers can ignore them.
    """
    g = load().g
    root = _resolve(paper_id, prefer_type="Paper")
    if root is None:
        logger.warning("citation_chain: paper %r not found", paper_id)
        return {"root": None, "depth": depth, "edges": []}
    edges: List[Dict[str, Any]] = []
    seen = {root}
    frontier = deque([(root, 0)])
    while frontier:
        node, hop = frontier.popleft()
        if hop >= depth:
            continue
        for _, tgt, data in g.out_edges(node, data=True):
            if data.get("type") != "CITES":
                continue
            tdata = g.nodes[tgt]
            edges.append({"from": node, "to": tgt,
                          "to_label": tdata.get("label"),
                          "stub": bool(tdata.get("stub")), "hop": hop + 1})
            if tgt not in seen:
                seen.add(tgt)
                frontier.append((tgt, hop + 1))
    return {"root": root, "depth": depth, "edges": edges}


def _datasets_of_method(g, method_id: str) -> Dict[str, str]:
    """Datasets a method was evaluated on = EVALUATES_ON targets of every paper
    that INTRODUCES/USES it. Returns {dataset_id: dataset_label}."""
    out: Dict[str, str] = {}
    for paper, _, data in g.in_edges(method_id, data=True):
        if data.get("type") not in ("INTRODUCES", "USES"):
            continue
        for _, ds, edata in g.out_edges(paper, data=True):
            if edata.get("type") == "EVALUATES_ON":
                out[ds] = g.nodes[ds].get("label")
    return out


def shared_datasets(method_a: str, method_b: str) -> List[Dict[str, Any]]:
    """Datasets BOTH methods were evaluated on (the basis for comparability)."""
    g = load().g
    a = _resolve(method_a, prefer_type="Method")
    b = _resolve(method_b, prefer_type="Method")
    if a is None or b is None:
        logger.warning("shared_datasets: %r or %r not found", method_a, method_b)
        return []
    da, db = _datasets_of_method(g, a), _datasets_of_method(g, b)
    return [{"id": ds, "label": da[ds]} for ds in da if ds in db]


def coverage_gaps() -> List[Dict[str, Any]]:
    """Seed for the Layer 5 Research Gap agent.

    A gap is a (method, dataset) pair where a *sibling* method -- one that
    shares at least one evaluation dataset with this method -- was evaluated on
    ``dataset`` but this method was not. In other words: "method X's peers all
    report on dataset D; X never did." Each gap names the sibling(s) that did,
    so the agent can frame the missing comparison.
    """
    g = load().g
    methods = [n for n, d in g.nodes(data=True) if d.get("type") == "Method"]
    ds_of = {m: set(_datasets_of_method(g, m)) for m in methods}

    gaps: List[Dict[str, Any]] = []
    for m in methods:
        mine = ds_of[m]
        if not mine:
            continue
        # siblings share at least one dataset with m (so a comparison is meaningful)
        siblings = [o for o in methods if o != m and (ds_of[o] & mine)]
        # datasets a sibling used that m did not
        for sib in siblings:
            for ds in ds_of[sib] - mine:
                gaps.append({
                    "method": g.nodes[m].get("label"), "method_id": m,
                    "missing_dataset": g.nodes[ds].get("label"), "dataset_id": ds,
                    "evaluated_by": g.nodes[sib].get("label"),
                })
    return gaps
