"""The structured output every analytical agent emits: the Finding.

Mirrors the house style (plain dataclasses). ref.md §3.6 (A2A) says agents
exchange *structured outputs, not free-form text* -- the Finding is that
structure. Each agent turns its reasoning into one or more Findings, which the
CLI persists to storage/findings.jsonl and which the Layer 6 coordinator passes
between agents and cross-validates.

A single shape covers all four agents; ``kind`` says which produced it and
``details`` carries the agent-specific payload, so downstream code (Layer 6,
the frontend) can treat findings uniformly while still drilling in.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

# Every finding kind an agent can emit. Layer 6 / the frontend validate against
# this so a typo'd kind fails loudly instead of silently matching nothing.
FINDING_KINDS = ("contradiction", "synergy", "gap", "hypothesis", "evidence")


@dataclass
class Finding:
    """One analytical result, with provenance back to the corpus.

    ``id`` is content-derived (agent + hash of summary/provenance) so the same
    finding from the same inputs gets the same id -- handy for dedup when the
    coordinator merges findings from several agents.
    """
    id: str
    agent: str                                  # the agent that produced it
    kind: str                                   # one of FINDING_KINDS
    summary: str                                # one-line human-readable result
    confidence: str = "low"                     # "high" | "medium" | "low"
    provenance: List[str] = field(default_factory=list)   # paper/claim/method ids
    details: Dict[str, Any] = field(default_factory=dict)  # kind-specific payload
    stub: bool = False                          # True if produced by the offline stub
    created_at: str = ""

    @staticmethod
    def make(agent: str, kind: str, summary: str, *, confidence: str = "low",
             provenance: List[str] = None, details: Dict[str, Any] = None,
             stub: bool = False) -> "Finding":
        """Build a Finding with a deterministic id and a UTC timestamp."""
        provenance = provenance or []
        key = f"{agent}|{kind}|{summary}|{'|'.join(sorted(provenance))}"
        fid = f"{agent}:{hashlib.sha1(key.encode('utf-8')).hexdigest()[:10]}"
        return Finding(
            id=fid, agent=agent, kind=kind, summary=summary,
            confidence=confidence, provenance=provenance,
            details=details or {}, stub=stub,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
