"""Structured outputs of the coordination layer.

ref.md §3.6: agents exchange *structured outputs, not free-form text*, enabling
cross-validation, multi-step pipelines, and separation of responsibilities. The
coordinator consumes Layer 5 Findings and produces:

  * CrossValidation -- a link it derived between two findings from *different*
    agents (e.g. a flagged contradiction whose papers also appear in the
    aggregated evidence), and
  * Report -- the consolidated result of investigating one topic: every
    finding, every cross-validation link, and a deterministic summary.

Both are plain dataclasses; findings are embedded as dicts so a Report is one
self-contained JSON object (persisted to storage/reports.jsonl).
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class CrossValidation:
    """A relationship the coordinator found between two agents' findings."""
    type: str                                   # e.g. "contradiction_vs_evidence"
    note: str                                   # human-readable explanation
    finding_ids: List[str] = field(default_factory=list)   # the linked findings
    confidence: str = "medium"


@dataclass
class Report:
    """The consolidated result of investigating one topic across all agents."""
    id: str
    topic: str
    created_at: str
    offline: bool
    agent_counts: Dict[str, int] = field(default_factory=dict)
    findings: List[Dict[str, Any]] = field(default_factory=list)        # Finding dicts
    cross_validations: List[Dict[str, Any]] = field(default_factory=list)  # CrossValidation dicts
    summary: str = ""

    @staticmethod
    def make(topic: str, offline: bool, findings: List[Dict[str, Any]],
             cross_validations: List[Dict[str, Any]], summary: str,
             agent_counts: Dict[str, int]) -> "Report":
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        rid = "report:" + hashlib.sha1(f"{topic}|{created}".encode()).hexdigest()[:10]
        return Report(id=rid, topic=topic, created_at=created, offline=offline,
                      agent_counts=agent_counts, findings=findings,
                      cross_validations=cross_validations, summary=summary)
