"""The LLM behind the agents that need bespoke reasoning.

Two of the four agents reuse Layer 4 tools that already do their LLM work
(Contradiction -> tools.detect_contradictions, Research Gap ->
tools.generate_hypotheses + coverage_gaps). The other two -- Synergy and
Evidence Aggregation -- need judgements Layer 4 doesn't expose, so they go
through a Reasoner defined here.

Rather than copy Layer 4's Hugging Face plumbing a third time, we **subclass**
it: `layer4` has no hyphen, so it imports normally, and Layer 4's HFReasoner /
FakeReasoner already carry the chat-completion call (`_complete_json`), the
429/5xx backoff, the HF_TOKEN check, and the offline-stub contract. We just add
two task methods -- `find_synergies` and `weigh_evidence` -- and their stubs.
Layer 5's Config exposes the same attribute names HFReasoner reads, so passing
it straight in Just Works.
"""

import json
import logging
from typing import Any, Dict, List

from layer4.reasoner import FakeReasoner as _L4Fake
from layer4.reasoner import HFReasoner as _L4HF

from .config import Config

logger = logging.getLogger(__name__)


_SYNERGY_SYSTEM = """\
You are the synergy-detection reasoner of a research-paper intelligence system.
You are given a topic and a numbered list of methods (name + description), each
from some paper. Identify pairs of methods that are COMPLEMENTARY -- that could
plausibly be COMBINED to get a benefit neither has alone (e.g. one supplies a
signal the other lacks, or they address different failure modes).

Be conservative: two methods that merely target the same task are NOT a synergy.
Returning an empty list is correct when there is no real complementarity.

Respond with JSON only, no prose, matching exactly:
{"synergies": [
  {"method_a": <int index>, "method_b": <int index>,
   "rationale": "<how combining them helps>", "confidence": "high"|"medium"|"low"}
]}"""

_EVIDENCE_SYSTEM = """\
You are the evidence-aggregation reasoner of a research-paper intelligence
system. Given a proposition/topic and a numbered list of claims (each from a
paper), weigh how the corpus bears on the proposition. Classify each claim as
supporting, contradicting, or neutral, then give an overall verdict.

Respond with JSON only, no prose, matching exactly:
{"verdict": "supported"|"contested"|"insufficient",
 "supporting": [<int index>, ...],
 "contradicting": [<int index>, ...],
 "summary": "<one or two sentences weighing the evidence>",
 "confidence": "high"|"medium"|"low"}"""


class AgentReasoner(_L4HF):
    """Real reasoning via HF, inheriting all of Layer 4's call machinery."""

    def find_synergies(self, topic: str,
                       methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        listing = "\n".join(
            f"[{i}] {m.get('name')}: {m.get('description') or m.get('text') or ''}"
            for i, m in enumerate(methods))
        user = f"Topic: {topic}\n\nMethods:\n{listing}"
        data = self._complete_json(_SYNERGY_SYSTEM, user)
        out = []
        for item in data.get("synergies", []):
            a, b = item.get("method_a"), item.get("method_b")
            if not (isinstance(a, int) and isinstance(b, int)):
                continue
            if not (0 <= a < len(methods) and 0 <= b < len(methods)) or a == b:
                continue
            out.append({"method_a": methods[a], "method_b": methods[b],
                        "rationale": item.get("rationale", ""),
                        "confidence": item.get("confidence", "low")})
        return out

    def weigh_evidence(self, topic: str,
                       claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        listing = "\n".join(
            f"[{i}] ({c.get('paper_id')}) {c.get('statement')}"
            for i, c in enumerate(claims))
        user = f"Proposition / topic: {topic}\n\nClaims:\n{listing}"
        data = self._complete_json(_EVIDENCE_SYSTEM, user)
        if not data:
            return {}
        # map indices back to claims for a self-contained result
        def pick(key):
            return [claims[i] for i in data.get(key, [])
                    if isinstance(i, int) and 0 <= i < len(claims)]
        return {"verdict": data.get("verdict", "insufficient"),
                "supporting": pick("supporting"),
                "contradicting": pick("contradicting"),
                "summary": data.get("summary", ""),
                "confidence": data.get("confidence", "low")}


class FakeAgentReasoner(_L4Fake):
    """Offline stub: structured placeholders, flagged ``stub: true``."""

    def find_synergies(self, topic: str,
                       methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(methods) < 2:
            return []
        a, b = methods[0], methods[1]
        return [{"method_a": a, "method_b": b,
                 "rationale": "OFFLINE STUB: real synergy judgement needs "
                              "HF_TOKEN. The two methods most associated with "
                              "the topic are surfaced as a candidate pair only.",
                 "confidence": "low", "stub": True}]

    def weigh_evidence(self, topic: str,
                       claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"verdict": "insufficient",
                "supporting": claims,           # can't judge stance offline
                "contradicting": [],
                "summary": f"OFFLINE STUB: gathered {len(claims)} claim(s) on "
                           f"'{topic}'; real evidence weighing needs HF_TOKEN.",
                "confidence": "low", "stub": True}


def get_agent_reasoner(config: Config, offline: bool = False):
    """Pick a reasoner. ``offline`` forces the stub; otherwise use the real HF
    reasoner but fall back to the stub (with a warning) when no HF_TOKEN is set,
    so the agents degrade instead of hard-failing -- same contract as Layer 4."""
    if offline:
        return FakeAgentReasoner(config)
    try:
        return AgentReasoner(config)
    except RuntimeError as exc:
        logger.warning("%s\n-> falling back to the offline stub reasoner.",
                       str(exc).splitlines()[0])
        return FakeAgentReasoner(config)
