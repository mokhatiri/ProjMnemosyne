"""The A2A coordinator: run the Layer 5 agents, then cross-validate findings.

This embodies ref.md §3.6 as a deterministic workflow (matching the rest of the
project's "code orchestrates, models judge" stance):

  1. Separation of responsibilities -- each Layer 5 agent does its own job
     (contradiction / synergy / gap / evidence) and returns structured Findings.
  2. Multi-step pipeline -- the coordinator runs them all on one topic and
     collects the findings.
  3. Cross-validation -- it then *relates findings from different agents* to
     corroborate or enrich them, without any extra LLM call: the links are
     derived from the findings' own structure (provenance, method names, etc.).

The cross-checks implemented:
  * contradiction x evidence -- a flagged contradiction whose two papers both
    appear in the topic's aggregated evidence is corroborated (and we attach the
    evidence verdict).
  * synergy x gap -- a proposed method combination that involves a method with a
    known coverage gap is noted as potentially addressing that gap too.

Findings are the only currency passed between layers -- never free text.
"""

import logging
from dataclasses import asdict
from typing import Dict, List, Optional

import layer5   # normal import: no hyphen in 'layer5'

from .config import Config
from .models import CrossValidation, Report

logger = logging.getLogger(__name__)


def _papers(provenance: List[str]) -> set:
    """The paper ids in a provenance list (drop unit ids like '...#claim:1' and
    'method:x')."""
    return {p for p in provenance
            if p and "#" not in p and not p.startswith(("method:", "dataset:"))}


class Coordinator:
    """Runs the agents and cross-validates their findings into a Report."""

    def __init__(self, config: Optional[Config] = None, offline: bool = False):
        self.config = config or Config()
        self.offline = offline

    def investigate(self, topic: str, k: Optional[int] = None) -> Report:
        """Full A2A pass over one topic."""
        logger.info("coordinator investigating %r (offline=%s)", topic, self.offline)
        # step 1+2: run every agent, collect structured findings
        findings = layer5.run_all(topic=topic, k=k, offline=self.offline)

        by_agent: Dict[str, int] = {}
        for f in findings:
            by_agent[f.agent] = by_agent.get(f.agent, 0) + 1

        # step 3: cross-validate findings across agents
        cvs = self._cross_validate(findings)

        summary = self._summarize(topic, findings, by_agent, cvs)
        return Report.make(
            topic=topic, offline=self.offline,
            findings=[asdict(f) for f in findings],
            cross_validations=[asdict(c) for c in cvs],
            summary=summary, agent_counts=by_agent)

    # --- cross-validation ------------------------------------------------------
    def _cross_validate(self, findings) -> List[CrossValidation]:
        contradictions = [f for f in findings if f.kind == "contradiction"]
        evidences = [f for f in findings if f.kind == "evidence"]
        synergies = [f for f in findings if f.kind == "synergy"]
        gaps = [f for f in findings if f.kind == "gap"]
        out: List[CrossValidation] = []

        # contradiction x evidence: are both conflicting papers in the evidence base?
        for c in contradictions:
            c_papers = _papers(c.provenance)
            for e in evidences:
                e_papers = set(e.provenance)
                if c_papers and c_papers <= e_papers:
                    out.append(CrossValidation(
                        type="contradiction_vs_evidence",
                        note=(f"Both papers in the contradiction also appear in "
                              f"the aggregated evidence on this topic "
                              f"(evidence verdict: {e.details.get('verdict')}). "
                              f"The flagged conflict is corroborated by the "
                              f"evidence base."),
                        finding_ids=[c.id, e.id], confidence="medium"))

        # synergy x gap: does a proposed combination involve a gap method?
        for s in synergies:
            names = {s.details.get("method_a", {}).get("name"),
                     s.details.get("method_b", {}).get("name")}
            names.discard(None)
            for g in gaps:
                gm = g.details.get("method")
                if gm and gm in names:
                    out.append(CrossValidation(
                        type="synergy_addresses_gap",
                        note=(f"The proposed synergy involves '{gm}', which has a "
                              f"coverage gap on '{g.details.get('missing_dataset')}'. "
                              f"Combining it may also help close that gap."),
                        finding_ids=[s.id, g.id], confidence="low"))
        return out

    @staticmethod
    def _summarize(topic, findings, by_agent, cvs) -> str:
        counts = ", ".join(f"{n} {a}" for a, n in sorted(by_agent.items()))
        verdict = next((f.details.get("verdict") for f in findings
                        if f.kind == "evidence"), None)
        parts = [f"Investigated '{topic}': {len(findings)} finding(s) across "
                 f"{len(by_agent)} agent(s)" + (f" ({counts})" if counts else "") + "."]
        if verdict:
            parts.append(f"Evidence verdict: {verdict}.")
        parts.append(f"{len(cvs)} cross-validation link(s) between agents.")
        if any(getattr(f, "stub", False) for f in findings):
            parts.append("(Some findings used the offline stub reasoner.)")
        return " ".join(parts)
