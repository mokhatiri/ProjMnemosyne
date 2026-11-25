"""The four analytical agents (ref.md §3.5).

Each is a workflow: gather structured evidence via Layer 4 tools / Layer 3-2
graph queries, apply a judgement (reusing a Layer 4 LLM tool, or a Layer 5
reasoner call), and emit Findings. None of them run an open-ended LLM loop.

  ContradictionAgent     conflicting claims across papers
  SynergyAgent           complementary methods that could combine
  ResearchGapAgent       method x dataset coverage gaps (+ grounded directions)
  EvidenceAggregationAgent   weigh supporting vs contradicting evidence

Provenance on every Finding points back to the corpus (paper / claim / method
ids) so Layer 6 and the frontend can trace and cross-check results.
"""

import logging
from typing import List, Optional

from .base import BaseAgent
from .models import Finding

logger = logging.getLogger(__name__)


class ContradictionAgent(BaseAgent):
    """Flags pairs of claims that conflict. Reuses Layer 4's
    detect_contradictions (which gathers topic-relevant claims and asks the LLM
    to judge); this agent drives it across seed topics and packages the results
    as Findings with provenance."""

    name = "contradiction"
    kind = "contradiction"

    def run(self, topic: Optional[str] = None, k: Optional[int] = None) -> List[Finding]:
        k = k or self.config.default_k
        topics = [topic] if topic else self._seed_topics()
        findings: List[Finding] = []
        seen = set()
        for tp in topics:
            res = self.tools.detect_contradictions(tp, k=k)
            for c in res.get("contradictions", []):
                a, b = c.get("claim_a", {}), c.get("claim_b", {})
                prov = [x for x in (a.get("paper_id"), b.get("paper_id"),
                                    a.get("chunk_id"), b.get("chunk_id")) if x]
                summary = (f"Possible contradiction between {a.get('paper_id')} "
                           f"and {b.get('paper_id')} regarding '{tp}'")
                f = Finding.make(
                    self.name, "contradiction", summary,
                    confidence=c.get("confidence", "low"), provenance=prov,
                    details={"topic": tp, "claim_a": a, "claim_b": b,
                             "explanation": c.get("explanation", "")},
                    stub=bool(c.get("stub")))
                if f.id not in seen:
                    seen.add(f.id)
                    findings.append(f)
        return findings

    def _seed_topics(self, limit: int = 5) -> List[str]:
        """When no topic is given, scan the corpus using each method as a seed."""
        methods = [m["label"] for m in self.graph_nodes("Method") if m["label"]]
        return methods[:limit] or [self.default_topic()]


class SynergyAgent(BaseAgent):
    """Identifies complementary methods that might be combined. Pulls the
    methods from the graph and asks the reasoner which pairs are genuinely
    complementary."""

    name = "synergy"
    kind = "synergy"

    def run(self, topic: Optional[str] = None, k: Optional[int] = None) -> List[Finding]:
        methods = [{"name": m["label"], "description": m.get("description"),
                    "paper_id": m.get("paper_id")}
                   for m in self.graph_nodes("Method") if m["label"]]
        if len(methods) < 2:
            logger.info("synergy: need >=2 methods in the graph, found %d", len(methods))
            return []
        tp = topic or "the corpus"
        findings: List[Finding] = []
        for s in self.reasoner.find_synergies(tp, methods):
            a, b = s.get("method_a", {}), s.get("method_b", {})
            # two methods from one paper are usually a method and its own
            # component or baseline, not a synergy worth proposing
            if a.get("paper_id") and a.get("paper_id") == b.get("paper_id"):
                logger.info("synergy: skipping same-paper pair %r + %r",
                            a.get("name"), b.get("name"))
                continue
            prov = [f"method:{a.get('name')}", f"method:{b.get('name')}"]
            summary = (f"Potential synergy: combine '{a.get('name')}' with "
                       f"'{b.get('name')}'")
            findings.append(Finding.make(
                self.name, "synergy", summary,
                confidence=s.get("confidence", "low"), provenance=prov,
                details={"topic": tp, "method_a": a, "method_b": b,
                         "rationale": s.get("rationale", "")},
                stub=bool(s.get("stub"))))
        return findings


class ResearchGapAgent(BaseAgent):
    """Surfaces under-explored method x dataset combinations from the knowledge
    graph (coverage_gaps), and reuses Layer 4's generate_hypotheses to turn the
    gap area into grounded research directions."""

    name = "gap"
    kind = "gap"

    def run(self, topic: Optional[str] = None, k: Optional[int] = None) -> List[Finding]:
        k = k or self.config.default_k
        findings: List[Finding] = []

        # 1. structured gaps straight from the graph (no LLM)
        gaps = self.safe_kg(lambda: self.kg.coverage_gaps(), [])
        for g in gaps:
            summary = (f"Coverage gap: '{g.get('method')}' was not evaluated on "
                       f"'{g.get('missing_dataset')}' although peer "
                       f"'{g.get('evaluated_by')}' was")
            findings.append(Finding.make(
                self.name, "gap", summary, confidence="medium",
                provenance=[g.get("method_id"), g.get("dataset_id")], details=g))

        # 2. grounded directions for the gap area (reuses Layer 4's LLM tool)
        tp = topic or (gaps[0]["method"] if gaps else self.default_topic())
        res = self.tools.generate_hypotheses(tp, k=k)
        for h in res.get("hypotheses", []):
            findings.append(Finding.make(
                self.name, "hypothesis", h.get("hypothesis", ""),
                confidence="low", provenance=[],
                details={"topic": tp, "rationale": h.get("rationale", ""),
                         "grounded_in": h.get("grounded_in", [])},
                stub=bool(h.get("stub"))))
        return findings


class EvidenceAggregationAgent(BaseAgent):
    """Weighs the supporting vs contradicting claims on a proposition/topic and
    returns a verdict with provenance."""

    name = "evidence"
    kind = "evidence"

    def run(self, topic: Optional[str] = None, k: Optional[int] = None) -> List[Finding]:
        tp = topic or self.default_topic()
        k = k or self.config.default_k
        res = self.tools.search_units(tp, kind="claim", k=k)
        claims = [{"paper_id": h["paper_id"], "statement": h["text"],
                   "chunk_id": h["chunk_id"]} for h in res["results"]]
        if not claims:
            logger.info("evidence: no claims found for '%s'", tp)
            return []
        verdict = self.reasoner.weigh_evidence(tp, claims)
        if not verdict:
            return []
        n_for = len(verdict.get("supporting", []))
        n_against = len(verdict.get("contradicting", []))
        summary = (f"Evidence on '{tp}': {verdict.get('verdict')} "
                   f"({n_for} supporting / {n_against} contradicting, "
                   f"from {len(claims)} claim(s))")
        prov = list(dict.fromkeys(c["paper_id"] for c in claims))
        return [Finding.make(
            self.name, "evidence", summary,
            confidence=verdict.get("confidence", "low"), provenance=prov,
            details={"topic": tp, **verdict}, stub=bool(verdict.get("stub")))]


# registry, so the CLI / Layer 6 can run agents by name
AGENTS = {a.name: a for a in
          (ContradictionAgent, SynergyAgent, ResearchGapAgent,
           EvidenceAggregationAgent)}


def run_agent(name: str, *, topic: Optional[str] = None, k: Optional[int] = None,
              offline: bool = False, config=None) -> List[Finding]:
    """Instantiate one agent by name and run it."""
    if name not in AGENTS:
        raise ValueError(f"unknown agent {name!r}; choose from {list(AGENTS)}")
    return AGENTS[name](config=config, offline=offline).run(topic=topic, k=k)


def run_all(*, topic: Optional[str] = None, k: Optional[int] = None,
            offline: bool = False, config=None) -> List[Finding]:
    """Run all four agents and concatenate their findings."""
    findings: List[Finding] = []
    for name in AGENTS:
        findings.extend(run_agent(name, topic=topic, k=k, offline=offline, config=config))
    return findings
