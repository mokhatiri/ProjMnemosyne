"""Layer 2 orchestrator: metadata.jsonl in, extracted.jsonl out.

Responsibilities (and only these -- parsing lives in tei_parser, LLM work in
extractor):

  1. read storage/metadata.jsonl and reduce it to unique papers
     (Layer 1 appends a line per run, so the same paper appears many times),
  2. skip papers that already have a line in storage/extracted.jsonl, which
     makes re-runs idempotent -- the run can be killed and restarted freely,
  3. parse each paper's TEI full text when it has one, falling back to
     abstract-only,
  4. fan extraction out over a small thread pool (papers are independent and
     the work is API-bound), and
  5. append results to storage/extracted.jsonl from the main thread only, so
     the append-only JSONL file needs no locking.
"""

import os
import json
import logging
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

from .config import Config
from .extractor import SYSTEM_PROMPT, Extractor
from .models import ExtractedPaper
from .tei_parser import TeiDocument, parse_tei_file

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Reading Layer 1's output
# ---------------------------------------------------------------------------

def load_papers(config: Config) -> List[dict]:
    """Read metadata.jsonl and return one dict per unique paper.

    Layer 1's sink is append-only, so a paper re-fetched across runs shows up
    once per run -- sometimes with a tei_path (the run that ingested the PDF)
    and sometimes without. We keep the *latest* record for each paper_id but
    carry an earlier tei_path forward if the latest record lacks one, so a
    metadata-only re-fetch never loses the full text.
    """
    path = config.metadata_path
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found -- run Layer 1 first (python -m layer1)")

    papers: Dict[str, dict] = {}   # paper_id -> record; dict preserves order
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
            # same primary key Layer 1 uses (Paper.paper_id property)
            pid = f"{record.get('source')}:{record.get('source_id')}"
            previous = papers.get(pid)
            if previous:
                old_tei = (previous.get("extra") or {}).get("tei_path")
                new_tei = (record.get("extra") or {}).get("tei_path")
                if old_tei and not new_tei:
                    record.setdefault("extra", {})["tei_path"] = old_tei
            papers[pid] = record
    return list(papers.values())


def load_extracted_ids(config: Config) -> set:
    """paper_ids that already have a line in extracted.jsonl (skip on re-run)."""
    done = set()
    if not os.path.exists(config.extracted_path):
        return done
    with open(config.extracted_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                done.add(json.loads(line)["paper_id"])
            except (json.JSONDecodeError, KeyError):
                continue   # a corrupt line just means that paper re-extracts
    return done


def append_extracted(config: Config, extracted: ExtractedPaper) -> None:
    """Append one ExtractedPaper to extracted.jsonl -- same append-only JSONL
    pattern as layer1/base_fetcher.store_metadata."""
    os.makedirs(config.local_storage_path, exist_ok=True)
    with open(config.extracted_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(extracted), ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Per-paper preparation (shared by the real run and --dry-run)
# ---------------------------------------------------------------------------

def prepare_paper(record: dict) -> Tuple[str, str, str, Optional[TeiDocument]]:
    """Resolve what text we have for one metadata record.

    Returns (paper_id, title, abstract, tei_doc-or-None). A None tei_doc means
    abstract-only extraction: either the paper never had a PDF/GROBID pass, or
    its TEI file is missing/malformed (parse_tei_file already logged why).
    """
    pid = f"{record.get('source')}:{record.get('source_id')}"
    title = record.get("title") or ""
    abstract = record.get("abstract") or ""
    tei_path = (record.get("extra") or {}).get("tei_path")
    doc = parse_tei_file(tei_path) if tei_path else None
    if doc:
        # GROBID's abstract is sentence-segmented and cleaned; prefer it when
        # present, otherwise keep the metadata abstract
        abstract = doc.abstract or abstract
    return pid, title, abstract, doc


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(config: Config, limit: Optional[int] = None,
        paper_id: Optional[str] = None, dry_run: bool = False) -> None:
    """Run extraction over everything pending in metadata.jsonl."""
    papers = load_papers(config)
    done = load_extracted_ids(config)
    logger.info("loaded %d unique papers, %d already extracted",
                len(papers), len(done))

    # --- select what to work on -------------------------------------------
    if paper_id:
        papers = [p for p in papers
                  if f"{p.get('source')}:{p.get('source_id')}" == paper_id]
        if not papers:
            print(f"paper id {paper_id!r} not found in {config.metadata_path}")
            return
    pending = [p for p in papers
               if f"{p.get('source')}:{p.get('source_id')}" not in done]
    skipped = len(papers) - len(pending)
    if skipped:
        print(f"(skipping {skipped} already-extracted paper(s); "
              f"delete their lines from {config.extracted_path} to redo)")
    if limit is not None:
        pending = pending[:limit]
    if not pending:
        print("Nothing to extract.")
        return

    # --- dry run: show the prompts, never touch the API ----------------------
    if dry_run:
        _dry_run(config, pending)
        return

    # constructing the Extractor checks HF_TOKEN and raises a clear error
    # before any thread is started
    extractor = Extractor(config)

    print(f"=== Extracting {len(pending)} paper(s) with {config.model} ===")
    ok = failed = 0
    with ThreadPoolExecutor(max_workers=config.max_workers) as pool:
        futures = {}
        for record in pending:
            pid, title, abstract, doc = prepare_paper(record)
            sections = doc.sections if doc else []
            futures[pool.submit(extractor.extract, pid, title,
                                abstract, sections)] = pid
        for fut in as_completed(futures):
            pid = futures[fut]
            try:
                extracted = fut.result()
            except Exception:   # one bad paper shouldn't sink the whole run
                logger.exception("extraction failed for %s", pid)
                failed += 1
                continue
            if extracted is None:    # invalid output even after retry
                failed += 1
                continue
            # writes happen here, on the main thread -- no file locking needed
            append_extracted(config, extracted)
            ok += 1
            print(f"  extracted {pid}: {extracted.unit_count()} units "
                  f"({len(extracted.claims)} claims, "
                  f"{len(extracted.methods)} methods, "
                  f"{len(extracted.datasets)} datasets, "
                  f"{len(extracted.results)} results, "
                  f"{len(extracted.assumptions)} assumptions, "
                  f"{len(extracted.limitations)} limitations) "
                  f"[{extracted.extraction_source}]")

    print(f"\nDone: {ok} extracted, {failed} failed/skipped. "
          f"Results appended to {config.extracted_path}")


def _dry_run(config: Config, pending: List[dict]) -> None:
    """Parse TEI and print the exact prompts, without calling the API.

    Reuses the Extractor's own prompt/chunking code so what you see is what a
    real run would send -- but builds prompts via a bare object to avoid the
    API-key check in Extractor.__init__.
    """
    preview = Extractor.__new__(Extractor)   # skip __init__ (no key needed)
    preview.config = config

    print(f"=== DRY RUN: {len(pending)} paper(s), model would be {config.model} ===")
    print(f"\n--- system prompt (shared by every call) ---\n{SYSTEM_PROMPT}")
    for record in pending:
        pid, title, abstract, doc = prepare_paper(record)
        sections = doc.sections if doc else []
        source = "tei_full_text" if sections else "abstract_only"
        prompts = preview.build_prompts(title, abstract, sections)
        print(f"\n=== {pid} [{source}] -> {len(prompts)} API call(s) ===")
        for i, prompt in enumerate(prompts, 1):
            print(f"\n--- user prompt {i}/{len(prompts)} "
                  f"(~{len(prompt) // 4} tokens) ---")
            print(prompt if len(prompt) <= 4000 else
                  prompt[:4000] + f"\n[... {len(prompt) - 4000} more characters ...]")
    print("\n(dry run complete -- no API calls were made, nothing was written)")
