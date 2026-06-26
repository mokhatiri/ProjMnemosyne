"""Layer 4: MCP (Model Context Protocol) Tool Layer (ref.md §3.5).

Exposes structured research-intelligence tools to LLMs/agents:

    search_papers, find_related_work, trace_citations,
    detect_contradictions, generate_hypotheses

The tools are plain importable functions (so Layer 5 agents can call them
directly) and are also served over real MCP by a thin FastMCP adapter
(`python -m layer4 serve`). The tool functions wrap Layer 3-1 (retrieval) and
Layer 3-2 (graph), reached via importlib because those packages have
hyphenated names. The two reasoning tools call the project's LLM (Hugging Face
Inference, as in Layer 2), with an offline stub when no key is present.

    from layer4 import tools
    tools.search_papers("chain of thought reasoning", k=5)
"""

from .config import Config
from . import tools
from .tools import (
    configure, detect_contradictions, find_related_work, generate_hypotheses,
    search_papers, trace_citations, TOOLS, TOOLS_BY_NAME,
)
from .reasoner import FakeReasoner, HFReasoner, get_reasoner

__all__ = [
    "Config",
    "tools",
    "configure",
    "search_papers",
    "find_related_work",
    "trace_citations",
    "detect_contradictions",
    "generate_hypotheses",
    "TOOLS",
    "TOOLS_BY_NAME",
    "HFReasoner",
    "FakeReasoner",
    "get_reasoner",
]
