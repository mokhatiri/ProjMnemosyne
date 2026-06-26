"""Build the knowledge graph from Layer 1 + Layer 2 output.

This is the heart of Layer 3-2. It reads metadata.jsonl (papers) and
extracted.jsonl (units), resolves recurring entity names to single nodes, and
emits the Node/Edge set that graph_store.py persists.

The build is **idempotent by full rebuild**: the graph is 100% derived data, so
rather than diffing and patching an existing graph (fiddly, easy to drift out
of sync), every run reconstructs it from scratch. Deterministic node ids
(models.py) make that cheap and always-consistent.

Pipeline:
  1. read both JSONL files, latest-line-wins (the Layer 3-1 pattern)
  2. normalize method/dataset names so spelling variants collapse to one node
  3. emit nodes + edges using those normalized ids, then hand them to the
     GraphStore

Entity resolution is normalization + a small alias table only. ref.md presents
the Embedding/Retrieval layer (3-1) and this Knowledge Graph layer (3-2) as
parallel modular components, both downstream of Layer 2 -- so this layer
deliberately does NOT reach into 3-1's vector store. Keeping it decoupled means
a graph build can never fail because of another layer's state (e.g. a missing
embedding API key), and the dependency graph stays a clean DAG. If semantic
name-merging is ever wanted at scale, add it here as a strictly optional step
that degrades to normalization-only -- never as a hard dependency.
"""

import os
import re
import json
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .config import Config
from .graph_store import GraphStore
from .models import Edge, Node

logger = logging.getLogger(__name__)


# ===========================================================================
# Reading the upstream JSONL files (mirrors layer3-1/index.py _read_latest_by_id)
# ===========================================================================

def _read_latest_by_id(path: str, id_of: Callable[[dict], str]) -> Dict[str, dict]:
    """Append-only JSONL -> {id: latest record}. Same contract as Layer 3-1."""
    records: Dict[str, dict] = {}
    with open(path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                logger.warning("skipping malformed line %d of %s: %s",
                               line_no, path, exc)
                continue
            records[id_of(record)] = record
    return records


def _paper_id(record: dict) -> str:
    """Primary key, identical to layer1.models.Paper.paper_id."""
    return f"{record.get('source')}:{record.get('source_id')}"


# ===========================================================================
# Entity-name normalization (pass 1 of entity resolution)
# ===========================================================================

# Leading qualifier words to drop: "the BERT model" / "a transformer" -> the
# substantive name. Matched as whole leading tokens, not substrings.
_QUALIFIER_TOKENS = {"the", "a", "an", "our", "their"}

# Hand-curated equivalences, applied as an exact match on the *fully normalized*
# string (so they can never fire mid-word). This is where domain knowledge that
# normalization alone can't capture lives -- acronyms and known synonyms. Keep
# it conservative: every entry risks a false merge.
_ALIAS_TABLE = {
    "cot": "chain of thought prompting",
    "chain of thought": "chain of thought prompting",
    "kd": "knowledge distillation",
    "sft": "supervised fine tuning",
    "llm": "large language model",
    "llms": "large language model",
}


def normalize(name: str) -> str:
    """Collapse a surface name to its canonical normalized form.

    lowercase -> punctuation to spaces -> collapse whitespace -> strip leading
    qualifier tokens -> apply the alias table. The result is what the node id
    is built from, so two spellings that normalize the same become one node.
    """
    if not name:
        return ""
    s = re.sub(r"[^a-z0-9]+", " ", name.lower())
    s = re.sub(r"\s+", " ", s).strip()
    tokens = s.split(" ")
    while tokens and tokens[0] in _QUALIFIER_TOKENS:
        tokens = tokens[1:]
    s = " ".join(tokens)
    return _ALIAS_TABLE.get(s, s)


# ===========================================================================
# The build itself
# ===========================================================================

@dataclass
class BuildReport:
    """Human-facing summary of a build, printed by the CLI."""
    papers_total: int = 0
    papers_extracted: int = 0
    papers_without_units: int = 0
    stub_papers: int = 0
    resolution: str = "normalization + alias table (no semantic merge)"
    node_counts: Dict[str, int] = field(default_factory=dict)
    edge_counts: Dict[str, int] = field(default_factory=dict)


def _result_index(extracted: dict) -> Dict[str, dict]:
    """Map normalized dataset name -> the result reported on it (for attaching
    metric/value to EVALUATES_ON edges). Last result on a dataset wins."""
    index: Dict[str, dict] = {}
    for res in extracted.get("results") or []:
        ds = res.get("dataset")
        if ds:
            index[normalize(ds)] = res
    return index


def build(config: Config) -> Tuple[GraphStore, BuildReport]:
    """Read inputs, resolve entities, and return a populated GraphStore."""
    if not os.path.exists(config.metadata_path):
        raise FileNotFoundError(
            f"{config.metadata_path} not found -- run Layer 1 first")
    papers = _read_latest_by_id(config.metadata_path, _paper_id)
    extracted = ({} if not os.path.exists(config.extracted_path)
                 else _read_latest_by_id(config.extracted_path,
                                         lambda r: r["paper_id"]))
    report = BuildReport(papers_total=len(papers), papers_extracted=len(extracted))
    logger.info("loaded %d papers, %d with extracted units",
                len(papers), len(extracted))

    # accumulate everything in plain dicts/lists first; the merge remap (pass 2)
    # is applied to these before they go into networkx
    nodes: Dict[str, Node] = {}
    edges: List[Edge] = []

    def ensure(node: Node) -> Node:
        """Insert node if new; otherwise fold the surface spelling in as an
        alias and keep the richest attrs. Returns the live node."""
        existing = nodes.get(node.id)
        if existing is None:
            nodes[node.id] = node
            return node
        existing.add_alias(node.label)
        for key, val in node.attrs.items():
            existing.attrs.setdefault(key, val)
        # a real paper supersedes a citation stub of the same id
        if existing.attrs.get("stub") and not node.attrs.get("stub"):
            existing.attrs["stub"] = False
            existing.label = node.label
        return existing

    # --- resolution index for CITES: many keys -> one canonical paper_id -------
    ref_index: Dict[str, str] = {}

    def _register_ref_keys(pid: str, record: dict) -> None:
        """All identifiers by which this paper might be *cited* by another."""
        def put(key):
            if key:
                ref_index[str(key).lower()] = pid
        put(pid)
        # merged records can carry slash-joined source/source_id -- index parts
        for part in str(record.get("source_id") or "").split("/"):
            put(part)
        put(record.get("doi"))
        for ext_key, ext_val in (record.get("extra", {}).get("externalIds") or {}).items():
            put(ext_val)
            # bare arXiv id, with and without version suffix
            if ext_key.lower() == "arxiv" and ext_val:
                put(re.sub(r"v\d+$", "", str(ext_val)))

    for pid, record in papers.items():
        _register_ref_keys(pid, record)

    # --- Paper + Author nodes, AUTHORED + CITES edges -------------------------
    for pid, record in papers.items():
        ensure(Node(
            id=f"paper:{pid}", type="Paper",
            label=record.get("title") or pid,
            attrs={
                "paper_id": pid,
                "year": _year_of(record.get("published")),
                "categories": record.get("categories") or [],
                "doi": record.get("doi"),
                "stub": False,
            }))

        for author in record.get("authors") or []:
            norm = normalize(author)
            if not norm:
                continue
            # authors are resolved by EXACT normalized name only -- never
            # semantically (two different people can have similar embeddings)
            anode = ensure(Node(id=f"author:{norm}", type="Author", label=author))
            anode.add_alias(author)
            edges.append(Edge(f"author:{norm}", f"paper:{pid}", "AUTHORED"))

        # references are sparse and often point outside the corpus; resolve what
        # we can, keep the rest as stub Paper nodes so the citation isn't lost
        for ref in record.get("references") or []:
            target_pid = ref_index.get(str(ref).lower())
            if target_pid:
                target_id = f"paper:{target_pid}"
            else:
                target_id = f"paper:{ref}"
                ensure(Node(id=target_id, type="Paper", label=str(ref),
                            attrs={"stub": True}))
                report.stub_papers += 1
            edges.append(Edge(f"paper:{pid}", target_id, "CITES"))

    # --- unit nodes/edges for extracted papers --------------------------------
    for pid, ex in extracted.items():
        paper_node_id = f"paper:{pid}"
        if not nodes.get(paper_node_id) or nodes[paper_node_id].attrs.get("stub"):
            # extracted record for a paper not in metadata.jsonl -- make a node
            ensure(Node(id=paper_node_id, type="Paper",
                        label=ex.get("title") or pid,
                        attrs={"paper_id": pid, "stub": False}))

        # claims -> Claim nodes + MAKES_CLAIM
        for i, claim in enumerate(ex.get("claims") or []):
            cid = f"claim:{pid}:{i}"
            ensure(Node(id=cid, type="Claim",
                        label=claim.get("statement") or "",
                        attrs={"claim_type": claim.get("claim_type"),
                               "confidence": claim.get("confidence"),
                               "evidence": claim.get("evidence"),
                               "section": claim.get("section"),
                               "paper_id": pid}))
            edges.append(Edge(paper_node_id, cid, "MAKES_CLAIM"))

        # methods -> Method nodes + INTRODUCES / USES
        for method in ex.get("methods") or []:
            name = method.get("name") or ""
            norm = normalize(name)
            if not norm:
                continue
            mid = f"method:{norm}"
            mnode = ensure(Node(id=mid, type="Method", label=name,
                                attrs={"role": method.get("role"),
                                       "description": method.get("description")}))
            mnode.add_alias(name)
            rel = "INTRODUCES" if method.get("role") == "introduced" else "USES"
            edges.append(Edge(paper_node_id, mid, rel,
                              attrs={"section": method.get("section")}))

        # datasets -> Dataset nodes + EVALUATES_ON (with metric/value when known)
        results = _result_index(ex)
        for ds in ex.get("datasets") or []:
            name = ds.get("name") or ""
            norm = normalize(name)
            if not norm:
                continue
            did = f"dataset:{norm}"
            dnode = ensure(Node(id=did, type="Dataset", label=name,
                                attrs={"purpose": ds.get("purpose")}))
            dnode.add_alias(name)
            attrs = {"section": ds.get("section")}
            match = results.get(norm)
            if match:   # dataset name lines up with a reported result
                attrs["metric"] = match.get("metric")
                attrs["value"] = match.get("value")
                attrs["baseline"] = match.get("baseline")
            edges.append(Edge(paper_node_id, did, "EVALUATES_ON", attrs=attrs))

    # --- ABOUT edges: Claim -> Method | Dataset it names ----------------------
    edges.extend(_about_edges(nodes))

    # --- hand off to the store -----------------------------------------------
    store = GraphStore()
    for node in nodes.values():
        store.add_node(node)
    seen = set()
    for edge in edges:
        # a merge can collapse an edge onto a self-loop or create duplicates;
        # drop both so the graph stays clean
        if edge.source == edge.target:
            continue
        key = (edge.source, edge.target, edge.type)
        if key in seen:
            continue
        seen.add(key)
        store.add_edge(edge)

    # --- finalize the report --------------------------------------------------
    real_papers = [n for n in nodes.values()
                   if n.type == "Paper" and not n.attrs.get("stub")]
    report.papers_without_units = sum(
        1 for n in real_papers if n.attrs.get("paper_id") not in extracted)
    report.node_counts = store.nodes_by_type_counts()
    report.edge_counts = store.edges_by_type()
    return store, report


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _year_of(published: Optional[str]) -> Optional[int]:
    """Published year from Layer 1's date strings ('2026-06-09T...' or '2022')."""
    if published and str(published)[:4].isdigit():
        return int(str(published)[:4])
    return None


def _entity_spellings(node: Node) -> List[str]:
    """Every normalized phrase that names an entity (canonical + aliases),
    long enough to match on without generating noise."""
    forms = {normalize(node.label)}
    forms.update(normalize(a) for a in node.aliases)
    return [f for f in forms if len(f) >= 3]


def _about_edges(nodes: Dict[str, Node]) -> List[Edge]:
    """Link each Claim to any Method/Dataset whose name it mentions.

    Matching is phrase-level on the normalized claim text (statement +
    evidence), padded with spaces so a name only matches on word boundaries
    (" gsm8k " not "agsm8kb"). Cheap and good enough at this corpus size.
    """
    targets = [(nid, n, _entity_spellings(n))
               for nid, n in nodes.items() if n.type in ("Method", "Dataset")]
    out: List[Edge] = []
    for nid, node in nodes.items():
        if node.type != "Claim":
            continue
        haystack = " " + normalize(
            (node.label or "") + " " + (node.attrs.get("evidence") or "")) + " "
        for tid, _, spellings in targets:
            if any(f" {s} " in haystack for s in spellings):
                out.append(Edge(nid, tid, "ABOUT"))
    return out
