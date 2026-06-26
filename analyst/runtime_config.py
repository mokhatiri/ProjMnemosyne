"""Live, editable runtime configuration for the autonomous analyst.

The static :class:`analyst.config.Config` holds *defaults* (read once at import).
This module holds the part of the analyst's behaviour that a human should be able
to change *while it runs* -- pace (interval/batch), whether it grows the corpus
each generation, and crucially **what it ingests**: which sources and the raw
per-source query strings. It is persisted to ``storage/analyst_config.json`` so
the setting survives restarts and is shared by the CLI, the frontend supervisor,
and (when growing) the pipeline subprocess.

Design notes
------------
* One flat JSON dict, merged over :data:`DEFAULTS` on load, so adding a key later
  is backward compatible (old files just pick up the new default).
* ``queries`` mirrors ``layer1.__main__.SOURCE_QUERIES`` -- each source speaks a
  different query language (arXiv ``search_query`` syntax, S2 free text,
  OpenReview venue id), so it's a per-source map, not one global string.
* No validation beyond types/clamping here; the supervisor is the single writer
  in practice and clamps user input before saving.
"""

import os
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Default per-source queries -- kept in sync with layer1.__main__.SOURCE_QUERIES.
# (Duplicated rather than imported to avoid importing a hyphen-free sibling that
# pulls the fetchers/network stack in just to read three strings.)
DEFAULT_QUERIES: Dict[str, str] = {
    "arxiv": "cat:cs.AI",                          # arXiv search_query
    "semantic_scholar": "large language models",   # S2 free-text query
    "openreview": "ICLR.cc/2024/Conference",       # OpenReview venue id
}

DEFAULTS: Dict[str, Any] = {
    "interval_seconds": 900,    # gap between generations (the "wait")
    "batch_size": 4,            # analysis tasks worked per generation
    "grow": 0,                  # papers ingested per generation (0 = don't grow)
    "limit": 5,                 # max papers requested per source when growing
    "offline": False,           # use the stub reasoner (no HF_TOKEN)
    "sources": ["arxiv"],       # which sources to ingest from when growing
    "queries": dict(DEFAULT_QUERIES),
}

ALL_SOURCES = list(DEFAULT_QUERIES)


def _path(storage_path: str = "./storage") -> str:
    return os.path.join(storage_path, "analyst_config.json")


def load(storage_path: str = "./storage") -> Dict[str, Any]:
    """Return the persisted config merged over the defaults (defaults if absent)."""
    cfg = {**DEFAULTS, "queries": dict(DEFAULT_QUERIES)}
    path = _path(storage_path)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                stored = json.load(fh)
            cfg.update({k: v for k, v in stored.items() if k != "queries"})
            if isinstance(stored.get("queries"), dict):
                cfg["queries"].update(stored["queries"])
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("could not read %s (%s); using defaults", path, exc)
    return cfg


def save(cfg: Dict[str, Any], storage_path: str = "./storage") -> Dict[str, Any]:
    """Persist a (sanitised) config and return what was written."""
    clean = sanitise(cfg)
    os.makedirs(storage_path, exist_ok=True)
    with open(_path(storage_path), "w", encoding="utf-8") as fh:
        json.dump(clean, fh, indent=2)
    return clean


def sanitise(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Coerce/clamp an incoming (possibly partial, possibly hostile) config dict
    into a complete, well-typed one. Unknown keys are dropped."""
    base = load()  # start from current-persisted-or-default, then overlay

    def _int(key, lo, hi):
        try:
            base[key] = max(lo, min(hi, int(cfg[key])))
        except (KeyError, TypeError, ValueError):
            pass

    _int("interval_seconds", 0, 86_400)   # 0 = no wait (back-to-back generations)
    _int("batch_size", 1, 50)
    _int("grow", 0, 25)
    _int("limit", 1, 100)

    if "offline" in cfg:
        base["offline"] = bool(cfg["offline"])

    if isinstance(cfg.get("sources"), list):
        picked = [s for s in cfg["sources"] if s in ALL_SOURCES]
        base["sources"] = picked or ["arxiv"]   # never leave it empty

    if isinstance(cfg.get("queries"), dict):
        for src, q in cfg["queries"].items():
            if src in ALL_SOURCES and isinstance(q, str) and q.strip():
                base["queries"][src] = q.strip()

    return base
