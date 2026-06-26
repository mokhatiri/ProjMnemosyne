"""ProjMnemosyne frontend: a minimal stdlib HTTP console over Layers 4-6.

    python -m frontend            # then open http://127.0.0.1:8000

See server.py for the endpoint list. No web framework / no build step -- one
static page (static/index.html) and a handful of JSON endpoints.
"""

from .server import run

__all__ = ["run"]
