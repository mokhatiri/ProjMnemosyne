"""Layer 3-1 (Embedding & Retrieval) CLI.

Builds and queries the local vector store over everything Layers 1+2 put in
storage/. Indexing is idempotent: re-runs only embed chunks not yet stored.

Run from the project root (the folder containing `layer3-1/`):

    python -m layer3-1 index                      # embed everything new
    python -m layer3-1 index --limit 5            # at most 5 papers
    python -m layer3-1 index --fake-embeddings    # no API key needed (testing)
    python -m layer3-1 search "chain of thought reasoning"
    python -m layer3-1 search "fine-tuning targets" --kind claim -k 5
    python -m layer3-1 more-like arxiv:2606.11189v1

Indexing needs VOYAGE_API_KEY in the environment (except --fake-embeddings);
searching reuses whatever model built the store.

(Note: `python -m layer3-1` works fine despite the hyphen -- the interpreter
resolves the module name at runtime, where any importable name is allowed.
Only the *import statement* chokes on hyphens, which is why this package uses
relative imports internally and external callers go through importlib --
see search.py.)
"""

import sys
import argparse
import logging

# Load API tokens from a .env file in the project root if present, so secrets
# (HF_TOKEN, VOYAGE_API_KEY, S2_API_KEY) can live there instead of being
# exported in every shell. Shell-set vars take precedence (load_dotenv never
# overrides os.environ); python-dotenv is optional -- if it isn't installed,
# the .env is simply ignored.
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from .config import Config
from .index import run_index
from .models import CHUNK_KINDS, SearchHit

# Same Windows-console fix as Layer 2: paper text is full of characters the
# legacy cp1252 codepage can't print.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def print_hits(hits) -> None:
    """Render search hits: rank, score, kind, id, then a one-line preview."""
    if not hits:
        print("  (no hits)")
        return
    for rank, hit in enumerate(hits, 1):
        preview = hit.chunk.text.replace("\n", " ")
        if len(preview) > 110:
            preview = preview[:110] + "..."
        print(f"  {rank:>2}. {hit.score:6.4f}  [{hit.chunk.kind}] "
              f"{hit.chunk.chunk_id}")
        print(f"      {preview}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m layer3-1",
        description="Layer 3-1 embedding & retrieval pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="chunk + embed everything new in storage/")
    p_index.add_argument("--limit", type=int, default=None, metavar="N",
                         help="index at most N papers (default: all)")
    p_index.add_argument("--fake-embeddings", action="store_true",
                         help="deterministic hash vectors instead of the Voyage "
                              "API (pipeline testing without a key)")

    p_search = sub.add_parser("search", help="semantic search over the store")
    p_search.add_argument("query", help="natural-language query text")
    p_search.add_argument("--kind", choices=CHUNK_KINDS, default=None,
                          help="restrict to one chunk kind (granularity)")
    p_search.add_argument("-k", type=int, default=10, help="number of hits")
    p_search.add_argument("--category", default=None,
                          help="filter by paper category, e.g. cs.LG")
    p_search.add_argument("--year", type=int, default=None,
                          help="filter by published year")

    p_more = sub.add_parser("more-like", help="papers related to a given paper")
    p_more.add_argument("paper_id", help="e.g. arxiv:2606.11189v1")
    p_more.add_argument("-k", type=int, default=10, help="number of hits")

    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    config = Config()

    if args.command == "index":
        run_index(config, limit=args.limit, fake=args.fake_embeddings)
        return

    # Imported lazily so `index` never touches the search singletons. Note:
    # `from . import search` would NOT work here -- __init__.py re-exports the
    # search *function*, which shadows the submodule of the same name on the
    # package object -- so we import the two functions directly.
    from .search import more_like, search as semantic_search

    if args.command == "search":
        filters = {}
        if args.category:
            filters["category"] = args.category
        if args.year:
            filters["year"] = args.year
        hits = semantic_search(args.query, k=args.k, kind=args.kind, **filters)
        scope = f" [kind={args.kind}]" if args.kind else ""
        print(f"\n=== top {len(hits)} for {args.query!r}{scope} ===")
        print_hits(hits)

    elif args.command == "more-like":
        hits = more_like(args.paper_id, k=args.k)
        print(f"\n=== papers related to {args.paper_id} ===")
        print_hits(hits)


if __name__ == "__main__":
    main()
