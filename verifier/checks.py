"""Deterministic checks of one insight against the corpus it claims to come from.

The agents (Layer 5) let an LLM judge; nothing checked the result before the
analyst banked it. These checks need no LLM: they test that an insight is
*traceable* (everything it cites exists and says what the insight quotes) and
*well-formed for its kind* (a contradiction spans two papers, a synergy joins
methods from different papers, an evidence verdict matches its own counts).
They cannot tell whether a judgement is wise -- only whether it stands on the
corpus. An insight with any error fails; warnings are reported but pass.
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


@dataclass
class Corpus:
    """What the checks look things up in: the Layer 3-1 chunks."""
    chunks: Dict[str, dict]                       # chunk_id -> chunk
    papers: Set[str]                              # paper ids
    methods: Dict[str, Set[str]]                  # normalised method name -> paper ids
    text_by_paper: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_chunks(cls, rows: Iterable[dict]) -> "Corpus":
        chunks, papers, methods, text = {}, set(), {}, {}
        for c in rows:
            chunks[c["chunk_id"]] = c
            papers.add(c["paper_id"])
            text[c["paper_id"]] = text.get(c["paper_id"], "") + " " + _norm(c["text"])
            if c["kind"] == "method":
                name = (c.get("metadata") or {}).get("name") or c["text"].split(":", 1)[0]
                methods.setdefault(_norm(name), set()).add(c["paper_id"])
        return cls(chunks, papers, methods, text)

    @classmethod
    def load(cls, storage_path: str = "./storage") -> "Corpus":
        path = os.path.join(storage_path, "chunks.jsonl")
        with open(path, encoding="utf-8") as fh:
            return cls.from_chunks(json.loads(l) for l in fh if l.strip())


@dataclass
class Verdict:
    insight_id: str
    kind: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors


def _check_claim_ref(ref: dict, corpus: Corpus, label: str, v: Verdict) -> Optional[str]:
    """A cited claim must exist, belong to the stated paper, and match its text.
    Returns the paper id it belongs to (None when unresolvable)."""
    cid = (ref or {}).get("chunk_id")
    chunk = corpus.chunks.get(cid) if cid else None
    if chunk is None:
        v.errors.append(f"{label}: cited chunk {cid!r} not in the corpus")
        return None
    if ref.get("paper_id") and ref["paper_id"] != chunk["paper_id"]:
        v.errors.append(f"{label}: chunk {cid} belongs to {chunk['paper_id']}, not {ref['paper_id']}")
    stmt = _norm(ref.get("statement", ""))
    if stmt and stmt not in _norm(chunk["text"]):
        v.errors.append(f"{label}: quoted statement differs from the stored text of {cid}")
    return chunk["paper_id"]


def _pair_key(*ids: str) -> Tuple[str, ...]:
    return tuple(sorted(ids))


def check(ins: dict, corpus: Corpus, seen_pairs: Optional[Set[tuple]] = None) -> Verdict:
    """Check one insight. ``seen_pairs`` carries the claim/method pairs already
    accepted (across the banked set) to catch mirrored duplicates; it is
    updated in place when the insight passes."""
    kind = ins.get("kind", "")
    v = Verdict(ins.get("id", "?"), kind)
    d = ins.get("details") or {}
    seen_pairs = seen_pairs if seen_pairs is not None else set()
    pair = None

    if ins.get("stub"):
        v.warnings.append("produced by the offline stub, not the LLM reasoner")

    for p in ins.get("provenance") or []:
        if not p or p.startswith(("method:", "dataset:")):
            continue
        if "#" in p:
            if p not in corpus.chunks:
                v.errors.append(f"provenance chunk {p!r} not in the corpus")
        elif p not in corpus.papers:
            v.errors.append(f"provenance paper {p!r} not in the corpus")

    if kind == "contradiction":
        pa = _check_claim_ref(d.get("claim_a"), corpus, "claim_a", v)
        pb = _check_claim_ref(d.get("claim_b"), corpus, "claim_b", v)
        ca, cb = (d.get("claim_a") or {}).get("chunk_id"), (d.get("claim_b") or {}).get("chunk_id")
        if ca and ca == cb:
            v.errors.append("both sides are the same claim")
        elif pa and pb and pa == pb:
            v.errors.append(f"both claims come from the same paper ({pa}): not a cross-paper contradiction")
        if ca and cb:
            pair = ("contradiction",) + _pair_key(ca, cb)

    elif kind == "synergy":
        sides = []
        for label in ("method_a", "method_b"):
            m = d.get(label) or {}
            name = _norm(m.get("name", ""))
            found = corpus.methods.get(name, set())
            if m.get("paper_id"):
                found = found | {m["paper_id"]} if m["paper_id"] in corpus.papers else found
            if not found:
                v.errors.append(f"{label} {m.get('name')!r} is not a method in the corpus")
            elif not m.get("paper_id"):
                v.warnings.append(f"{label} {m.get('name')!r} carries no paper_id (resolved by name)")
            sides.append(found)
        if all(sides) and len(sides[0] | sides[1]) == 1:
            v.errors.append(f"both methods come from the same paper ({next(iter(sides[0]))}): "
                            "one is part of, or built on, the other")
        names = [_norm((d.get(x) or {}).get("name", "")) for x in ("method_a", "method_b")]
        if all(names):
            pair = ("synergy",) + _pair_key(*names)

    elif kind == "evidence":
        sup, con = d.get("supporting") or [], d.get("contradicting") or []
        for i, ref in enumerate(sup):
            _check_claim_ref(ref, corpus, f"supporting[{i}]", v)
        for i, ref in enumerate(con):
            _check_claim_ref(ref, corpus, f"contradicting[{i}]", v)
        m = re.search(r"\((\d+) supporting / (\d+) contradicting", ins.get("summary", ""))
        if m and (int(m.group(1)), int(m.group(2))) != (len(sup), len(con)):
            v.errors.append(f"summary counts {m.group(1)}/{m.group(2)} differ from the lists {len(sup)}/{len(con)}")
        verdict = d.get("verdict")
        if verdict == "supported" and len(sup) <= len(con):
            v.errors.append(f"verdict 'supported' with {len(sup)} supporting vs {len(con)} contradicting")
        if verdict == "supported" and len(sup) < 2:
            v.warnings.append("verdict 'supported' rests on fewer than 2 claims")
        if not sup and not con:
            v.warnings.append("no claim cited on either side")
        pair = ("evidence", _norm(d.get("topic", "")),
                tuple(sorted(r.get("chunk_id", "") for r in sup)),
                tuple(sorted(r.get("chunk_id", "") for r in con)))

    elif kind == "hypothesis":
        grounded = d.get("grounded_in") or []
        if not grounded:
            v.errors.append("hypothesis cites nothing it is grounded in")
        for g in grounded:
            mm = re.match(r"\s*(\S+)\s*(?:\((.*)\))?\s*$", g or "")
            pid, entity = (mm.group(1), mm.group(2)) if mm else (g, None)
            if pid not in corpus.papers:
                v.errors.append(f"grounded_in paper {pid!r} not in the corpus")
            elif entity and _norm(entity) not in corpus.text_by_paper.get(pid, ""):
                v.errors.append(f"{entity!r} does not appear in the units of {pid}")

    if pair is not None:
        if pair in seen_pairs:
            v.errors.append("duplicate of an insight already accepted (same pair, other order or wording)")
        elif v.passed:
            seen_pairs.add(pair)
    return v


def check_all(insights: List[dict], corpus: Corpus,
              seen: Optional[Set[tuple]] = None) -> List[Verdict]:
    """Check insights in order; ``seen`` (optional) collects the pairs of the
    ones that pass, so later batches can be checked for duplicates."""
    seen = set() if seen is None else seen
    return [check(i, corpus, seen) for i in insights]
