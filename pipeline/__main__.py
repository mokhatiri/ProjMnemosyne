"""Top-level pipeline runner: build the whole stack, then serve the console.

Run from the project root:

    python -m pipeline                       # extract -> index -> graph -> serve UI
    python -m pipeline --ingest 2            # also fetch+ingest 2 papers first (L1)
    python -m pipeline --investigate "chain of thought"   # run an A2A report too
    python -m pipeline --no-serve            # build only, don't launch the console
    python -m pipeline --offline --fake-embeddings        # no API keys needed
    python -m pipeline --port 9000

Build steps run as the individual layer CLIs (so you see each layer's output);
the frontend is served in-process at the end. The orchestrator is key-aware:
it uses real extraction/embeddings when HF_TOKEN / VOYAGE_API_KEY are set
(loaded from .env) and skips or falls back otherwise, reusing the corpus on disk.
"""

import sys
import argparse
import logging

# Load API tokens from .env (so key-awareness below sees them). Optional;
# shell-set vars win. Same block as the layer CLIs.
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from .config import Config
from .runner import run_pipeline

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def parse_args(config: Config) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m pipeline",
        description="Run the full ProjMnemosyne pipeline, then launch the frontend console.")
    p.add_argument("--ingest", type=int, default=0, metavar="N",
                   help="fetch + fully ingest N papers via Layer 1 first "
                        "(default 0 = skip; reuse existing corpus)")
    p.add_argument("--sources", nargs="+", default=config.default_sources,
                   help="Layer 1 sources when --ingest is used")
    p.add_argument("--query", action="append", default=[], metavar="SOURCE=QUERY",
                   help="override a source's search query, e.g. --query arxiv=cat:cs.LG "
                        "(repeatable; passed through to Layer 1)")
    p.add_argument("--limit", type=int, default=None,
                   help="cap papers processed by L1/L2/L3-1")
    p.add_argument("--skip-extract", action="store_true", help="skip Layer 2")
    p.add_argument("--skip-index", action="store_true", help="skip Layer 3-1")
    p.add_argument("--skip-graph", action="store_true", help="skip Layer 3-2")
    p.add_argument("--fake-embeddings", action="store_true",
                   help="force deterministic fake embeddings in Layer 3-1")
    p.add_argument("--offline", action="store_true",
                   help="stub the LLM reasoning (Layer 6 investigate + frontend)")
    p.add_argument("--investigate", default=None, metavar="TOPIC",
                   help="also run a Layer 6 A2A investigation on TOPIC")
    p.add_argument("--no-serve", action="store_true",
                   help="build only; don't launch the frontend console")
    p.add_argument("--host", default=config.host)
    p.add_argument("--port", type=int, default=config.port)
    p.add_argument("--keep-going", action="store_true",
                   help="continue past a failed build step")
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = Config()
    args = parse_args(config)
    # parse repeatable "SOURCE=QUERY" pairs into a {source: query} map
    queries = {}
    for item in args.query:
        source, _, query = item.partition("=")
        if source.strip() and query.strip():
            queries[source.strip()] = query.strip()
    code = run_pipeline(
        ingest=args.ingest, sources=args.sources, queries=queries, limit=args.limit,
        skip_extract=args.skip_extract, skip_index=args.skip_index,
        skip_graph=args.skip_graph, fake_embeddings=args.fake_embeddings,
        offline=args.offline, investigate=args.investigate,
        serve=not args.no_serve, host=args.host, port=args.port,
        keep_going=args.keep_going)
    sys.exit(code)


if __name__ == "__main__":
    main()
