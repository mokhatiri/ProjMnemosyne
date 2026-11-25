"""The Layer 4 tool surface (ref.md §3.5): structured tools an LLM/agent calls.

Five tools, each a plain function returning JSON-serialisable dicts:

    search_papers          paper-level semantic search
    find_related_work      similar papers + citation + shared-method neighbours
    trace_citations        walk the CITES graph
    detect_contradictions  (LLM) flag conflicting claims on a topic
    generate_hypotheses    (LLM) propose grounded research directions

The first three are pure accessors over Layer 3-1 (retrieval) and Layer 3-2
(graph). The last two gather evidence the same way, then hand it to the
Reasoner (reasoner.py) for the LLM judgement.

Two robustness choices make this layer dependable as other systems' tool
surface:
  * Cross-package imports go through importlib, because Layer 3-1/3-2 live in
    hyphenated package names (`layer3-1`) that a normal `import` can't name.
  * Every retrieval call degrades: if the Layer 3-1 vector store can't be
    queried (no embedding API key, empty/locked store -> it raises
    RuntimeError), we fall back to keyword scoring over the same chunks read
    straight from the JSONL files. Results are tagged ``match: "semantic"`` or
    ``match: "keyword"`` so the caller always knows which it got. A tool must
    not hard-fail just because a downstream key is missing.
"""

import re
import json
import logging
import importlib
from functools import lru_cache
from typing import Any, Dict, List, Optional

from .config import Config
from .reasoner import get_reasoner

logger = logging.getLogger(__name__)


# ===========================================================================
# Lazy wiring to the lower layers (imported once, cached)
# ===========================================================================

@lru_cache(maxsize=1)
def _retrieval():
    """Layer 3-1's public search API (search / more_like)."""
    return importlib.import_module("layer3-1.search")


@lru_cache(maxsize=1)
def _kg():
    """Layer 3-2's public query API (citation_chain, papers_using, ...)."""
    return importlib.import_module("layer3-2.queries")


# the reasoner is a configurable singleton: configure(offline=True) forces the
# stub before any tool runs (used by `--offline`); otherwise it's built on first
# use and self-degrades to the stub when HF_TOKEN is absent (see reasoner.py)
_reasoner_inst = None
_offline = False


def configure(offline: bool = False) -> None:
    """Set offline mode for the reasoning tools; resets the cached reasoner."""
    global _offline, _reasoner_inst
    _offline = offline
    _reasoner_inst = None


def _reasoner():
    global _reasoner_inst
    if _reasoner_inst is None:
        _reasoner_inst = get_reasoner(Config(), offline=_offline)
    return _reasoner_inst


# ===========================================================================
# Keyword fallback -- reads the SAME chunks the vector store holds
# ===========================================================================

def _read_jsonl_latest(path: str, id_of) -> Dict[str, dict]:
    """Append-only JSONL -> {id: latest record} (the project-wide pattern)."""
    import os
    out: Dict[str, dict] = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                out[id_of(rec)] = rec
    return out


@lru_cache(maxsize=1)
def _all_chunks() -> List[Any]:
    """Every chunk in the corpus, built with Layer 3-1's own chunker so the
    keyword fallback searches exactly the units the vector store would."""
    cfg = Config()
    index = importlib.import_module("layer3-1.index")     # reuse build_chunks
    papers = _read_jsonl_latest(cfg.metadata_path,
                                lambda r: f"{r.get('source')}:{r.get('source_id')}")
    extracted = _read_jsonl_latest(cfg.extracted_path, lambda r: r["paper_id"])
    chunks: List[Any] = []
    for pid, rec in papers.items():
        chunks.extend(index.build_chunks(rec, extracted.get(pid)))
    return chunks


def _terms(text: str) -> List[str]:
    """Distinct lowercase word tokens (length >= 2) for keyword overlap."""
    return list({t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) >= 2})


def _passes(chunk, filters: Dict[str, Any]) -> bool:
    meta = chunk.metadata or {}
    if "paper_id" in filters and chunk.paper_id != filters["paper_id"]:
        return False
    if "year" in filters and meta.get("year") != int(filters["year"]):
        return False
    if "category" in filters and filters["category"] not in (meta.get("categories") or []):
        return False
    return True


def _keyword_search(query: str, kind: Optional[str], k: int,
                    filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Score chunks by query-term overlap. Deterministic, no API needed."""
    terms = _terms(query)
    if not terms:
        return []
    scored = []
    for ch in _all_chunks():
        if kind and ch.kind != kind:
            continue
        if not _passes(ch, filters):
            continue
        hay = ch.text.lower()
        matched = sum(1 for t in terms if t in hay)
        if matched:
            scored.append((matched / len(terms), ch))
    scored.sort(key=lambda sc: sc[0], reverse=True)
    return [_chunk_dict(ch, round(score, 4)) for score, ch in scored[:k]]


def _chunk_dict(chunk, score: float) -> Dict[str, Any]:
    """Uniform hit dict, identical shape whether semantic or keyword."""
    return {"chunk_id": chunk.chunk_id, "paper_id": chunk.paper_id,
            "kind": chunk.kind, "text": chunk.text, "score": score,
            "metadata": chunk.metadata or {}}


def _hit_dict(hit) -> Dict[str, Any]:
    """Map a Layer 3-1 SearchHit to the same uniform hit dict."""
    return _chunk_dict(hit.chunk, round(hit.score, 4))


def _search(query: str, kind: Optional[str], k: int,
            **filters) -> tuple[List[Dict[str, Any]], str]:
    """Semantic search with a keyword fallback. Returns (hits, mode)."""
    try:
        hits = _retrieval().search(query, k=k, kind=kind, **filters)
        return [_hit_dict(h) for h in hits], "semantic"
    except RuntimeError as exc:
        logger.warning("semantic retrieval unavailable (%s); using keyword "
                       "fallback", str(exc).splitlines()[0])
        return _keyword_search(query, kind, k, filters), "keyword"


def _spread_across_papers(hits: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    """Keep the ranking order but take hits round-robin by paper (best hit of
    each paper first, then second-best, ...), up to k."""
    by_paper: Dict[str, List[Dict[str, Any]]] = {}
    for h in hits:
        by_paper.setdefault(h["paper_id"], []).append(h)
    out: List[Dict[str, Any]] = []
    depth = 0
    while len(out) < k and any(len(v) > depth for v in by_paper.values()):
        for group in by_paper.values():   # dicts keep first-seen (= rank) order
            if depth < len(group) and len(out) < k:
                out.append(group[depth])
        depth += 1
    return out


def _snippet(text: str, n: int = 200) -> str:
    s = " ".join(text.split())
    return s if len(s) <= n else s[:n] + "..."


def _safe_kg(call, default):
    """Run a Layer 3-2 query, tolerating a missing/!built graph (returns
    ``default`` and warns rather than raising into the tool caller)."""
    try:
        return call()
    except FileNotFoundError as exc:
        logger.warning("knowledge graph unavailable (%s); build it with "
                       "`python -m layer3-2 build`", exc)
        return default


# ===========================================================================
# The five tools
# ===========================================================================

def search_papers(query: str, k: int = 10, year: Optional[int] = None,
                  category: Optional[str] = None) -> Dict[str, Any]:
    """Find papers relevant to a query by semantic similarity of their
    title+abstract. Optionally filter by published `year` or arXiv `category`
    (e.g. "cs.LG"). Returns ranked papers with a relevance score and snippet.
    """
    filters: Dict[str, Any] = {}
    if year is not None:
        filters["year"] = year
    if category is not None:
        filters["category"] = category
    hits, mode = _search(query, kind="abstract", k=k, **filters)
    return {
        "query": query, "match": mode, "count": len(hits),
        "results": [{
            "paper_id": h["paper_id"],
            "title": h["metadata"].get("title"),
            "score": h["score"],
            "year": h["metadata"].get("year"),
            "categories": h["metadata"].get("categories"),
            "snippet": _snippet(h["text"]),
        } for h in hits],
    }


def find_related_work(paper_id: str, k: int = 10) -> Dict[str, Any]:
    """Given a paper id (e.g. "arxiv:2606.11189v1"), surface related work three
    ways: papers with similar abstracts (semantic), papers it cites (citation
    graph), and papers that share a method with it (knowledge graph).
    """
    similar, mode = _more_like(paper_id, k)
    cites = _safe_kg(lambda: _kg().citation_chain(paper_id, 1), {"edges": []})
    cited = [{"paper_id": e["to"].split("paper:", 1)[-1],
              "title": e["to_label"], "stub": e["stub"]}
             for e in cites.get("edges", [])]
    return {
        "paper_id": paper_id, "match": mode,
        "semantically_similar": similar,
        "cites": cited,
        "shares_methods": _co_method_papers(paper_id),
    }


def trace_citations(paper_id: str, depth: int = 2) -> Dict[str, Any]:
    """Walk the outgoing citation graph from a paper, breadth-first, up to
    `depth` hops. Citations to papers outside the corpus are returned as stubs
    (flagged), so the chain is never silently truncated.
    """
    chain = _safe_kg(lambda: _kg().citation_chain(paper_id, depth),
                     {"root": None, "depth": depth, "edges": []})
    edges = chain.get("edges", [])
    chain["resolved_count"] = sum(1 for e in edges if not e["stub"])
    chain["stub_count"] = sum(1 for e in edges if e["stub"])
    return chain


def detect_contradictions(topic: str, k: int = 8) -> Dict[str, Any]:
    """Gather the claims most relevant to `topic` from across papers, then use
    the reasoning model to flag pairs that genuinely contradict each other.
    Returns the candidate claims considered and any contradictions found.
    """
    # Over-fetch, then interleave papers: the plain top-k is often dominated by
    # one paper, which leaves the reasoner only same-paper pairs to judge.
    hits, mode = _search(topic, kind="claim", k=k * 3)
    hits = _spread_across_papers(hits, k)
    claims = [{"chunk_id": h["chunk_id"], "paper_id": h["paper_id"],
               "statement": h["text"],
               "claim_type": h["metadata"].get("claim_type")} for h in hits]
    found = _reasoner().find_contradictions(topic, claims) if claims else []
    # a contradiction is between papers; same-paper "tensions" are dropped
    found = [c for c in found
             if (c.get("claim_a") or {}).get("paper_id")
             != (c.get("claim_b") or {}).get("paper_id")]
    return {
        "topic": topic, "match": mode, "reasoner": _reasoner().model_name,
        "candidates_considered": len(claims),
        "contradictions": found,
    }


def generate_hypotheses(topic: str, k: int = 8) -> Dict[str, Any]:
    """Assemble grounding for `topic` -- relevant claims, relevant methods, and
    knowledge-graph coverage gaps -- then use the reasoning model to propose
    novel but grounded research hypotheses. Each hypothesis cites what it builds
    on.
    """
    claim_hits, mode = _search(topic, kind="claim", k=k)
    method_hits, _ = _search(topic, kind="method", k=k)
    gaps = _safe_kg(lambda: _kg().coverage_gaps(), [])
    grounding = {
        "claims": [{"paper_id": h["paper_id"], "statement": h["text"]}
                   for h in claim_hits],
        "methods": [{"paper_id": h["paper_id"], "text": h["text"]}
                    for h in method_hits],
        "coverage_gaps": gaps,
    }
    hyps = _reasoner().propose_hypotheses(topic, grounding)
    return {
        "topic": topic, "match": mode, "reasoner": _reasoner().model_name,
        "grounding_sizes": {"claims": len(grounding["claims"]),
                            "methods": len(grounding["methods"]),
                            "coverage_gaps": len(gaps)},
        "hypotheses": hyps,
    }


# ---------------------------------------------------------------------------
# helpers for find_related_work
# ---------------------------------------------------------------------------

def _more_like(paper_id: str, k: int) -> tuple[List[Dict[str, Any]], str]:
    """Similar papers by abstract. Semantic via Layer 3-1; on failure, keyword-
    search abstracts using this paper's own title+abstract as the query."""
    try:
        hits = _retrieval().more_like(paper_id, k=k)
        return [{"paper_id": h.chunk.paper_id,
                 "title": h.chunk.metadata.get("title"),
                 "score": round(h.score, 4)} for h in hits], "semantic"
    except RuntimeError:
        # fallback: use the paper's own abstract chunk text as the query
        own = next((c for c in _all_chunks()
                    if c.paper_id == paper_id and c.kind == "abstract"), None)
        if own is None:
            return [], "keyword"
        hits = _keyword_search(own.text, "abstract", k + 1,
                               {})  # +1 because the paper matches itself
        out = [{"paper_id": h["paper_id"], "title": h["metadata"].get("title"),
                "score": h["score"]} for h in hits if h["paper_id"] != paper_id]
        return out[:k], "keyword"


def _co_method_papers(paper_id: str) -> List[Dict[str, Any]]:
    """Papers that share an INTRODUCES/USES method with this paper."""
    kg = _kg()
    node = f"paper:{paper_id}"
    methods = _safe_kg(lambda: kg.neighbors(node), [])
    out, seen = [], {paper_id}
    for m in methods:
        if m.get("direction") != "out" or m.get("edge_type") not in ("INTRODUCES", "USES"):
            continue
        for p in _safe_kg(lambda mid=m["id"]: kg.papers_using(mid), []):
            other = p.get("label") and p["id"].split("paper:", 1)[-1]
            if other and other not in seen:
                seen.add(other)
                out.append({"paper_id": other, "title": p.get("label"),
                            "via_method": m.get("label"), "relation": p.get("relation")})
    return out


def search_units(query: str, kind: Optional[str] = None, k: int = 10,
                 **filters) -> Dict[str, Any]:
    """Lower-level search over chunks of a given `kind` ("claim", "method",
    "dataset", "abstract", ...), with the same semantic->keyword fallback as the
    named tools. Returns the raw hit dicts. This is a building block for the
    Layer 5 agents (e.g. gathering claims on a topic to weigh); it is public but
    deliberately NOT part of the five-tool MCP surface, which stays task-level.
    """
    hits, mode = _search(query, kind, k, **filters)
    return {"query": query, "kind": kind, "match": mode,
            "count": len(hits), "results": hits}


# ---------------------------------------------------------------------------
# registry -- consumed by the MCP server and the CLI
# ---------------------------------------------------------------------------

# Only the five task-level tools are exposed over MCP; search_units above is an
# internal building block for Layer 5, not an advertised tool.
TOOLS = [search_papers, find_related_work, trace_citations,
         detect_contradictions, generate_hypotheses]
TOOLS_BY_NAME = {fn.__name__: fn for fn in TOOLS}
