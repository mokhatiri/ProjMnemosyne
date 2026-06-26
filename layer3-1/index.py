"""Build pipeline: Layer 1/2 JSONL files -> chunks -> embeddings -> VectorStore.

For every paper this produces:
  * one "abstract" chunk (title + abstract) -- the paper-level granularity, and
  * one chunk per Layer 2 unit (claim/method/dataset/result/assumption/
    limitation) -- the unit-level granularity.

Chunk ids are deterministic (paper_id + kind + position), and chunk_ids
already present in the store are skipped, so re-running `index` only embeds
papers that arrived since the last run -- idempotent, like every other layer's
pipeline.
"""

import os
import json
import logging
from typing import Dict, List, Optional

from .config import Config
from .embedder import FakeEmbedder, VoyageEmbedder
from .models import Chunk
from .store import VectorStore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Reading the upstream JSONL files
# ---------------------------------------------------------------------------

def _read_latest_by_id(path: str, id_of) -> Dict[str, dict]:
    """Read an append-only JSONL file, keeping the *latest* record per id.

    Both upstream files are append-only sinks (Layer 1 re-appends papers on
    every run), so "latest line wins" recovers the current state. Returns an
    insertion-ordered dict {id: record}.
    """
    records: Dict[str, dict] = {}
    with open(path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                logger.warning("skipping malformed line %d of %s: %s",
                               line_no, path, exc)
                continue
            records[id_of(record)] = record
    return records


def load_papers(config: Config) -> Dict[str, dict]:
    """Unique papers from metadata.jsonl, keyed by paper_id."""
    if not os.path.exists(config.metadata_path):
        raise FileNotFoundError(
            f"{config.metadata_path} not found -- run Layer 1 first")
    return _read_latest_by_id(
        config.metadata_path,
        lambda r: f"{r.get('source')}:{r.get('source_id')}")


def load_extracted(config: Config) -> Dict[str, dict]:
    """ExtractedPaper records from extracted.jsonl, keyed by paper_id.
    Missing file is fine -- papers then get abstract-level chunks only."""
    if not os.path.exists(config.extracted_path):
        logger.warning("%s not found -- indexing abstracts only "
                       "(run Layer 2 to get unit-level chunks)",
                       config.extracted_path)
        return {}
    return _read_latest_by_id(config.extracted_path, lambda r: r["paper_id"])


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _year_of(published: Optional[str]) -> Optional[int]:
    """Published year from Layer 1's date strings ('2026-06-09T...' or '2022')."""
    if published and published[:4].isdigit():
        return int(published[:4])
    return None


def build_chunks(paper: dict, extracted: Optional[dict]) -> List[Chunk]:
    """All chunks for one paper: the abstract chunk + one per extracted unit.

    Every chunk shares the paper-level metadata (title, categories, year) so
    filters and result rendering work uniformly at both granularities; unit
    chunks add their own fields (section, claim_type, role, ...) on top.
    """
    paper_id = f"{paper.get('source')}:{paper.get('source_id')}"
    title = (paper.get("title") or "").strip()
    abstract = (paper.get("abstract") or "").strip()
    base_meta = {
        "title": title,
        "categories": paper.get("categories") or [],
        "year": _year_of(paper.get("published")),
    }
    chunks: List[Chunk] = []

    # --- paper level: one chunk for title + abstract -------------------------
    if title or abstract:
        chunks.append(Chunk(
            chunk_id=f"{paper_id}#abstract",
            paper_id=paper_id,
            kind="abstract",
            # title prepended: it carries a lot of retrieval signal and makes
            # the chunk readable on its own in search results
            text=f"{title}\n\n{abstract}".strip(),
            metadata=base_meta,
        ))

    if not extracted:
        return chunks   # paper not extracted yet -> paper-level only

    # --- unit level: one chunk per Layer 2 unit --------------------------------
    # Each entry: (extracted.jsonl key, chunk kind, text builder, extra meta keys).
    # The text builder turns the unit dict into the string that gets embedded;
    # remaining fields ride along as metadata instead of polluting the vector.
    unit_specs = [
        ("claims", "claim",
         lambda u: u["statement"],
         ("claim_type", "confidence", "evidence", "section")),
        ("methods", "method",
         lambda u: f"{u['name']}: {u['description']}" if u.get("description") else u["name"],
         ("name", "role", "section")),
        ("datasets", "dataset",
         lambda u: f"{u['name']}: {u['purpose']}" if u.get("purpose") else u["name"],
         ("name", "section")),
        ("results", "result",
         lambda u: (f"{u['metric']}: {u['value']}"
                    + (f" on {u['dataset']}" if u.get("dataset") else "")
                    + (f" (baseline: {u['baseline']})" if u.get("baseline") else "")),
         ("metric", "value", "dataset", "baseline", "section")),
        ("assumptions", "assumption",
         lambda u: u["statement"],
         ("basis", "section")),
        ("limitations", "limitation",
         lambda u: u["statement"],
         ("section",)),
    ]
    for key, kind, text_of, meta_keys in unit_specs:
        for i, unit in enumerate(extracted.get(key) or []):
            text = text_of(unit).strip()
            if not text:
                continue
            chunks.append(Chunk(
                # position-based suffix: stable because Layer 2 writes each
                # paper exactly once (idempotent skip on its side)
                chunk_id=f"{paper_id}#{kind}:{i}",
                paper_id=paper_id,
                kind=kind,
                text=text,
                metadata={**base_meta,
                          **{mk: unit.get(mk) for mk in meta_keys}},
            ))
    return chunks


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_index(config: Config, limit: Optional[int] = None,
              fake: bool = False) -> None:
    """Index everything new in storage/: chunk, embed, persist."""
    store = VectorStore(config)
    # FakeEmbedder needs no key; VoyageEmbedder raises a clear error without
    # one -- constructed before any work so the failure is immediate
    embedder = FakeEmbedder(config) if fake else VoyageEmbedder(config)

    papers = load_papers(config)
    extracted = load_extracted(config)
    logger.info("loaded %d papers, %d with extracted units",
                len(papers), len(extracted))

    paper_ids = list(papers)
    if limit is not None:
        paper_ids = paper_ids[:limit]

    # chunk everything, then keep only what the store hasn't seen
    new_chunks: List[Chunk] = []
    for pid in paper_ids:
        for chunk in build_chunks(papers[pid], extracted.get(pid)):
            if chunk.chunk_id not in store.ids:
                new_chunks.append(chunk)

    if not new_chunks:
        print(f"Nothing new to index ({len(store)} chunks already in the store).")
        return

    print(f"=== Indexing {len(new_chunks)} new chunks from {len(paper_ids)} "
          f"paper(s) with {embedder.model_name} ===")
    vectors = embedder.embed([c.text for c in new_chunks], input_type="document")
    store.add(new_chunks, vectors, embedder.model_name)

    # per-kind summary so a run's output shows the shape of what was indexed
    by_kind: Dict[str, int] = {}
    for chunk in new_chunks:
        by_kind[chunk.kind] = by_kind.get(chunk.kind, 0) + 1
    for kind, count in sorted(by_kind.items()):
        print(f"  {kind:<11} {count}")
    print(f"\nDone: store now holds {len(store)} chunks "
          f"({store.meta['model']}, dim={store.meta['dim']}) in "
          f"{config.vectors_path} + {config.chunks_path}")
