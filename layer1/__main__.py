"""Layer 1 (Data Ingestion) smoke test / demo pipeline.

Mirrors the Data Ingestion Layer described in ref.md §3.1: fetch papers from
several academic sources concurrently, deduplicate/merge records that describe
the same paper, then run each through the per-paper ingest pipeline
(store_pdf -> extract_text_from_pdf via GROBID -> store_metadata).

Run from the project root (the folder containing `layer1/`):

    python -m layer1                       # multi-source fetch + dedup, metadata only
    python -m layer1 --ingest 2            # also full-ingest the first 2 papers (PDF+GROBID)
    python -m layer1 --sources arxiv       # restrict to specific sources
    python -m layer1 --limit 10 --ingest 1

GROBID (full-text extraction) is optional: if it isn't running on
config.grobid_endpoint, ingest() still downloads the PDF, skips extraction
gracefully, and stores metadata.
"""

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
from .coordinator import FetchCoordinator
from .fetchers import ArxivFetcher, SemanticScholarFetcher, OpenReviewFetcher

# Per-source query strings. Each source speaks a different query language
# (see each fetcher's docstring), so the coordinator takes a per-source map.
SOURCE_QUERIES = {
    "arxiv": "cat:cs.AI",                         # arXiv search_query
    "semantic_scholar": "large language models",  # S2 free-text query
    "openreview": "ICLR.cc/2024/Conference",      # OpenReview venue id
}


def build_coordinator(config: Config, sources) -> FetchCoordinator:
    """Instantiate the requested fetchers and wrap them in a coordinator."""
    available = {
        "arxiv": ArxivFetcher,
        "semantic_scholar": SemanticScholarFetcher,
        "openreview": OpenReviewFetcher,
    }
    fetchers = [available[name](config) for name in sources]
    return FetchCoordinator(fetchers)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Layer 1 ingestion pipeline smoke test")
    parser.add_argument(
        "--sources", nargs="+", default=["arxiv"],
        choices=list(SOURCE_QUERIES),
        help="Which sources to query (default: arxiv only, to keep the smoke test fast).",
    )
    parser.add_argument(
        "--limit", type=int, default=5,
        help="Max results to request per source.",
    )
    parser.add_argument(
        "--ingest", type=int, default=0, metavar="N",
        help="Fully ingest the first N papers (download PDF + GROBID extract + store). "
             "Default 0 = metadata only, no PDF downloads.",
    )
    parser.add_argument(
        "--query", action="append", default=[], metavar="SOURCE=QUERY",
        help="Override the search query for a source, e.g. --query arxiv=cat:cs.LG "
             "or --query semantic_scholar='diffusion models'. Repeatable; sources "
             "left unspecified keep their default query.",
    )
    return parser.parse_args()


def resolve_queries(sources, overrides):
    """Per-source query map: CLI ``--query SOURCE=Q`` overrides win over the
    built-in SOURCE_QUERIES defaults. ``overrides`` is the raw list of
    ``"source=query"`` strings from argparse."""
    parsed = {}
    for item in overrides:
        source, _, query = item.partition("=")
        source, query = source.strip(), query.strip()
        if source in SOURCE_QUERIES and query:
            parsed[source] = query
        else:
            logging.getLogger(__name__).warning(
                "ignoring --query %r (unknown source or empty query)", item)
    return {name: parsed.get(name, SOURCE_QUERIES[name]) for name in sources}


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args() # get the arguments
    config = Config() # load the configuration (e.g. API endpoints, storage paths)

    coordinator = build_coordinator(config, args.sources) # start a coordinator with the requested sources
    queries = resolve_queries(args.sources, args.query) # per-source queries (CLI overrides win over defaults)

    # --- 1. Fan-out fetch + dedup/merge across sources (ref.md §3.1) ---
    # `limit` covers S2/OpenReview; `max_results` covers arXiv. Passing both is
    # harmless because each fetcher only reads the kwargs it understands.
    papers = coordinator.fetch_all(queries, limit=args.limit, max_results=args.limit)
    print(f"\n=== Fetched & merged {len(papers)} unique papers "
          f"from {', '.join(args.sources)} ===")
    for p in papers:
        also = p.extra.get("also_seen_in")
        seen = f"  (also in: {', '.join(also)})" if also else ""
        print(f"\n{p.paper_id} - {p.title}{seen}\n  {p.abstract[:100]} ...")

    # --- 2. Per-paper ingest pipeline (store_pdf -> extract -> store_metadata) ---
    if args.ingest <= 0:
        print("\n(skip ingestion: re-run with --ingest N to download PDFs and "
              "extract full text)")
        return

    # ingest() needs a fetcher instance (it owns the HTTP session / storage).
    # Any registered fetcher works; the pipeline itself is source-agnostic.
    worker = coordinator.get(args.sources[0])
    to_ingest = papers[: args.ingest]
    print(f"\n=== Ingesting {len(to_ingest)} papers "
          f"(PDF download + GROBID extraction + metadata store) ===")
    for p in to_ingest:
        worker.ingest(p)  # store_pdf -> extract_text_from_pdf -> store_metadata
        tei = p.extra.get("tei_path")
        status = f"TEI -> {tei}" if tei else "metadata only (no PDF / GROBID unavailable)"
        print(f"  ingested {p.paper_id}: {status}")

    print(f"\nDone. Metadata appended to {config.local_storage_path}/metadata.jsonl")

if __name__ == "__main__":
    print("\n=== Starting Layer 1 Ingestion Pipeline Smoke Test ===\n")
    main()
    print("\n=== Layer 1 Ingestion Pipeline Smoke Test Complete ===\n")
