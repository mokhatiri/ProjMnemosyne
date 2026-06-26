"""Layer 5: Analytical Agent Layer (ref.md §3.5).

Specialized agents that reason *over* the knowledge graph and retrieval by
calling the Layer 4 MCP tools, emitting structured Findings:

    ContradictionAgent, SynergyAgent, ResearchGapAgent, EvidenceAggregationAgent

Each is a deterministic workflow (no open-ended LLM loop). Findings are the
structured currency the Layer 6 coordinator (A2A) passes between agents.

    from layer5 import run_agent, run_all
    findings = run_agent("contradiction", topic="chain of thought")
"""

from .config import Config
from .models import FINDING_KINDS, Finding
from .reasoner import AgentReasoner, FakeAgentReasoner, get_agent_reasoner
from .base import BaseAgent, save_findings
from .agents import (
    AGENTS, ContradictionAgent, EvidenceAggregationAgent, ResearchGapAgent,
    SynergyAgent, run_agent, run_all,
)

__all__ = [
    "Config",
    "Finding",
    "FINDING_KINDS",
    "BaseAgent",
    "save_findings",
    "AgentReasoner",
    "FakeAgentReasoner",
    "get_agent_reasoner",
    "ContradictionAgent",
    "SynergyAgent",
    "ResearchGapAgent",
    "EvidenceAggregationAgent",
    "AGENTS",
    "run_agent",
    "run_all",
]
