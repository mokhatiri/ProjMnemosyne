"""Layer 6: Agent-to-Agent (A2A) Coordination Layer (ref.md §3.6).

Orchestrates the Layer 5 agents over a topic and cross-validates their
structured findings into one consolidated Report. Agents exchange Findings
(structured), never free-form text.

    from layer6 import Coordinator
    report = Coordinator(offline=True).investigate("chain of thought")
"""

from .config import Config
from .models import CrossValidation, Report
from .coordinator import Coordinator

__all__ = ["Config", "CrossValidation", "Report", "Coordinator"]
