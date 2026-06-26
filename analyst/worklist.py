"""Self-directed target selection: what should the analyst look at next?

This is the part that makes the loop *autonomous* -- instead of a human passing
`--topic`, the analyst derives its own to-do list from the current knowledge
graph. Each Task has a deterministic id so the engine knows what it has already
done and never repeats work; when the corpus grows (new methods appear in the
graph) new Tasks appear automatically on the next generation.

The task set, given the graph:
  * one global synergy probe (which methods complement each other),
  * one global research-gap probe (coverage_gaps over the whole graph),
  * per method, a contradiction probe and an evidence probe seeded on that
    method's name (methods are the substantive concepts the corpus is "about").
"""

import importlib
import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """One unit of analysis the engine can run. ``id`` is deterministic."""
    id: str
    agent: str                      # "contradiction" | "synergy" | "gap" | "evidence"
    topic: Optional[str]            # seed topic, or None for the global agents


def graph_method_labels() -> List[str]:
    """Method node labels from the knowledge graph (the concepts to seed on).
    Empty if the graph hasn't been built yet."""
    queries = importlib.import_module("layer3-2.queries")
    try:
        store = queries.load()
    except FileNotFoundError:
        logger.warning("knowledge graph not built; run the pipeline first "
                       "(python -m pipeline) -- analyst has nothing to scan")
        return []
    return sorted({data.get("label") for _, data in store.g.nodes(data=True)
                   if data.get("type") == "Method" and data.get("label")})


def build_tasks(method_labels: List[str]) -> List[Task]:
    """The full self-generated to-do list for the current graph."""
    tasks: List[Task] = [
        Task("synergy:*", "synergy", None),   # global: complementary methods
        Task("gap:*", "gap", None),           # global: coverage gaps
    ]
    for label in method_labels:
        tasks.append(Task(f"contradiction:{label}", "contradiction", label))
        tasks.append(Task(f"evidence:{label}", "evidence", label))
    return tasks
