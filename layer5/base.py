"""Shared machinery for the analytical agents.

Every agent is a *workflow*: a class whose run() drives a fixed, auditable
sequence of Layer 4 tool calls and (where needed) Layer 5 reasoner calls,
emitting structured Findings. They do not run open-ended LLM loops -- the
control flow lives in Python, which keeps them deterministic and testable
offline.

BaseAgent centralises the wiring the four agents share:
  * access to Layer 4's tools (imported normally -- `layer4` has no hyphen) and
    Layer 3-2's graph queries (imported via importlib -- `layer3-2` does),
  * a lazily-built reasoner (real HF, or the offline stub),
  * a helper to read node lists straight from the graph (for "scan the whole
    corpus" modes), and
  * persistence of Findings to storage/findings.jsonl.
"""

import os
import json
import logging
import importlib
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional

from .config import Config
from .models import Finding
from .reasoner import get_agent_reasoner

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for the four analytical agents."""

    name: str = "base"        # subclasses set; also the Finding.agent value
    kind: str = "evidence"    # default Finding kind for this agent

    def __init__(self, config: Optional[Config] = None, offline: bool = False):
        self.config = config or Config()
        self.offline = offline
        self._reasoner = None
        # make Layer 4's own reasoning tools (detect_contradictions /
        # generate_hypotheses) use the matching reasoner mode
        self.tools.configure(offline=offline)

    # --- lazy module accessors -------------------------------------------------
    @property
    def tools(self):
        """Layer 4's tool functions (search_units, detect_contradictions, ...)."""
        import layer4.tools as t      # normal import: no hyphen in 'layer4'
        return t

    @property
    def kg(self):
        """Layer 3-2's public graph queries (coverage_gaps, claims_about, ...)."""
        return importlib.import_module("layer3-2.queries")

    @property
    def reasoner(self):
        if self._reasoner is None:
            self._reasoner = get_agent_reasoner(self.config, self.offline)
        return self._reasoner

    # --- shared helpers --------------------------------------------------------
    def graph_nodes(self, node_type: str) -> List[Dict[str, Any]]:
        """All nodes of a type, as flat dicts. Used by agents that scan the
        whole corpus (e.g. Synergy over every Method). Empty if the graph
        hasn't been built."""
        try:
            store = self.kg.load()
        except FileNotFoundError:
            logger.warning("knowledge graph not built; run `python -m layer3-2 build`")
            return []
        out = []
        for nid, data in store.g.nodes(data=True):
            if data.get("type") == node_type:
                out.append({"id": nid, "label": data.get("label"),
                            "paper_id": data.get("paper_id"),
                            "description": data.get("description"),
                            "role": data.get("role")})
        return out

    def safe_kg(self, call: Callable, default):
        """Run a graph query, tolerating a missing/unbuilt graph."""
        try:
            return call()
        except FileNotFoundError as exc:
            logger.warning("knowledge graph unavailable (%s)", exc)
            return default

    def default_topic(self) -> str:
        """A reasonable seed when the caller gives no topic: the first method in
        the graph, else a generic fallback."""
        methods = self.graph_nodes("Method")
        return methods[0]["label"] if methods else "large language models"

    # --- contract --------------------------------------------------------------
    def run(self, **kwargs) -> List[Finding]:
        """Produce findings. Implemented by each agent."""
        raise NotImplementedError


def save_findings(config: Config, findings: List[Finding]) -> None:
    """Append findings to storage/findings.jsonl (the append-only house pattern)."""
    if not findings:
        return
    os.makedirs(config.local_storage_path, exist_ok=True)
    with open(config.findings_path, "a", encoding="utf-8") as fh:
        for f in findings:
            fh.write(json.dumps(asdict(f), ensure_ascii=False) + "\n")
    logger.info("saved %d finding(s) to %s", len(findings), config.findings_path)
