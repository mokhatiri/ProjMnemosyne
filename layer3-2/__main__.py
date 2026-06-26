"""Layer 3-2 (Knowledge Graph) CLI.

Builds and queries the knowledge graph over Layer 1 + Layer 2 output.

Run from the project root (the folder containing `layer3-2/`):

    python -m layer3-2 build                      # rebuild graph.json from scratch
    python -m layer3-2 stats                      # node/edge counts, top-degree nodes
    python -m layer3-2 query papers_using "TARGET-SFT"
    python -m layer3-2 query claims_about GSM8K
    python -m layer3-2 query citation_chain semantic_scholar:1b6e8... 2
    python -m layer3-2 query shared_datasets "TARGET-SFT" "Standard SFT"
    python -m layer3-2 query coverage_gaps
    python -m layer3-2 query neighbors paper:arxiv:2606.11189v1 MAKES_CLAIM

Building needs only the JSONL files in storage/. Semantic entity merging
additionally needs a *real* Layer 3-1 vector store; with a fake/absent store it
falls back to normalization-only resolution and says so.

(Note: `python -m layer3-2` works despite the hyphen -- the interpreter
resolves module names at runtime; only `import layer3-2` is a SyntaxError,
which is why this package uses relative imports and external callers go through
importlib -- see __init__.py.)
"""

import sys
import json
import argparse
import logging

from .config import Config
from .builder import build
from .graph_store import GraphStore

# Same Windows-console fix as Layers 2 and 3-1: graph labels are full of
# characters the legacy cp1252 codepage can't print.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def cmd_build(config: Config) -> None:
    """Rebuild the graph from scratch and persist it."""
    store, report = build(config)
    store.save(config.graph_path)

    print("\n=== Layer 3-2 build complete ===")
    print(f"papers (metadata):   {report.papers_total}")
    print(f"papers with units:   {report.papers_extracted}")
    print(f"papers without units:{report.papers_without_units}  "
          f"(no Layer 2 extraction yet -> Paper/Author/CITES only)")
    print(f"citation stub papers:{report.stub_papers}  "
          f"(cited ids not in the corpus)")
    print(f"entity resolution:   {report.resolution}")
    print("\nnodes by type:")
    for t, c in sorted(report.node_counts.items()):
        print(f"  {t:<13} {c}")
    print("edges by type:")
    for t, c in sorted(report.edge_counts.items()):
        print(f"  {t:<13} {c}")
    print(f"\nwrote {config.graph_path}")


def cmd_stats(config: Config) -> None:
    """Show counts + the highest-degree nodes (the graph's hubs)."""
    store = GraphStore.load(config.graph_path)
    g = store.g
    print("\n=== graph stats ===")
    print("nodes by type:")
    for t, c in sorted(store.nodes_by_type_counts().items()):
        print(f"  {t:<13} {c}")
    print("edges by type:")
    for t, c in sorted(store.edges_by_type().items()):
        print(f"  {t:<13} {c}")

    # top-degree nodes = the most connected entities (papers/methods usually)
    degree = sorted(g.degree(), key=lambda kv: kv[1], reverse=True)
    print("\ntop nodes by degree:")
    for node_id, deg in degree[:10]:
        data = g.nodes[node_id]
        label = (data.get("label") or "")[:55]
        print(f"  {deg:>3}  [{data.get('type')}] {node_id}")
        if label and label != node_id:
            print(f"       {label}")


# query name -> (callable, how many positional args, per-arg coercion)
def _query_table():
    from . import queries
    return {
        "neighbors":      (queries.neighbors, 1, 2),       # node_id [edge_type]
        "papers_using":   (queries.papers_using, 1, 1),
        "claims_about":   (queries.claims_about, 1, 1),
        "citation_chain": (queries.citation_chain, 1, 2),  # paper_id [depth]
        "shared_datasets":(queries.shared_datasets, 2, 2),
        "coverage_gaps":  (queries.coverage_gaps, 0, 0),
    }


def cmd_query(config: Config, fn: str, args: list) -> None:
    """Dispatch `query <fn> <args...>` to the public queries API."""
    from . import queries
    queries.load(config)   # seed the lazy singleton with the CLI's config
    table = _query_table()
    if fn not in table:
        print(f"unknown query {fn!r}. available: {', '.join(sorted(table))}")
        return
    func, min_args, max_args = table[fn]
    if not (min_args <= len(args) <= max_args):
        print(f"{fn} expects {min_args}..{max_args} arg(s), got {len(args)}")
        return
    # citation_chain's 2nd arg (depth) is an int; everything else stays a string
    call_args = list(args)
    if fn == "citation_chain" and len(call_args) == 2:
        call_args[1] = int(call_args[1])
    result = func(*call_args)
    print(f"\n=== {fn}({', '.join(map(repr, args))}) ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if isinstance(result, list):
        print(f"\n({len(result)} result(s))")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m layer3-2",
        description="Layer 3-2 knowledge-graph build & query")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="rebuild graph.json from the JSONL inputs")
    sub.add_parser("stats", help="node/edge counts and top-degree nodes")
    p_query = sub.add_parser("query", help="run a public query function")
    p_query.add_argument("fn", help="query name (e.g. papers_using)")
    p_query.add_argument("args", nargs="*", help="positional args for the query")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    config = Config()
    if args.command == "build":
        cmd_build(config)
    elif args.command == "stats":
        cmd_stats(config)
    elif args.command == "query":
        cmd_query(config, args.fn, args.args)


if __name__ == "__main__":
    main()
