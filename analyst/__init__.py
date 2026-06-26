"""ProjMnemosyne autonomous analyst.

The self-directed driver that turns the analytical capabilities (Layers 4-6)
into a system that *works on its own*: it loops slowly in the background, picks
its own targets from the knowledge graph, runs the Layer 5 agents, and
accumulates ranked insights -- unattended.

    python -m analyst run            # loop, slowly, forever
    python -m analyst insights       # see what it has found

Programmatic:
    from analyst import AnalysisEngine
    AnalysisEngine(offline=True).run(iterations=1)
"""

from .config import Config
from .engine import AnalysisEngine
from .worklist import Task, build_tasks

__all__ = ["Config", "AnalysisEngine", "Task", "build_tasks"]
