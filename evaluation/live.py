"""Live retrieval evaluation: re-embed with a chosen Voyage model, query like search().

    python -m evaluation.live --model voyage-4            # 11-paper and full pool
    python -m evaluation.live --model voyage-3 --model voyage-4-large
    python -m evaluation.live --model voyage-4 --distractors 300   # harder pool

For each model:
  1. Build a separate store under storage/eval/<model>/ with the project's own
     Layer 3-1 chunking (build_chunks) over EVERY paper in metadata.jsonl, so
     the candidate pool is the whole corpus, not only the extracted papers.
     Documents are embedded with input_type="document" (as `index` does).
     A store already built for that model is reused (no API calls).
  2. Embed every extracted unit's text with input_type="query" -- the exact
     path live search() takes -- and rank the paper abstracts.
  3. Report recall@1, recall@k, MRR with a random baseline, on two pools:
     the extracted papers only, and the full corpus.

Needs VOYAGE_API_KEY (.env). The committed storage/ store is never touched.
"""

import argparse
import importlib
import json
import os
import sys
import time

import numpy as np

from .retrieval import rank_source_papers, summarise, unit_rows

_cfg = importlib.import_module("layer3-1.config")
_store = importlib.import_module("layer3-1.store")
_index = importlib.import_module("layer3-1.index")
_emb = importlib.import_module("layer3-1.embedder")


def _load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


DISTRACTOR_QUERY = "cat:cs.CL OR cat:cs.LG OR cat:cs.AI"


def load_distractors(n: int, out_root: str) -> dict:
    """n recent arXiv papers fetched live through Layer 1's ArxivFetcher,
    cached in <out_root>/distractors.jsonl so every model sees the same pool."""
    if n <= 0:
        return {}
    os.makedirs(out_root, exist_ok=True)
    path = os.path.join(out_root, "distractors.jsonl")
    if not os.path.exists(path):
        from dataclasses import asdict
        l1_config = importlib.import_module("layer1.config")
        l1_arxiv = importlib.import_module("layer1.fetchers.arxiv")
        fetcher = l1_arxiv.ArxivFetcher(l1_config.Config())
        papers = []
        for start in range(0, n, 100):
            papers.extend(fetcher.fetch(DISTRACTOR_QUERY, max_results=min(100, n - start), start=start))
            time.sleep(3)   # arXiv API etiquette: one request every 3 s
        with open(path, "w", encoding="utf-8") as fh:
            for p in papers:
                fh.write(json.dumps(asdict(p), ensure_ascii=False) + "\n")
        print(f"fetched {len(papers)} distractor papers from arXiv -> {path}")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out[f"{r.get('source')}:{r.get('source_id')}"] = r
                if len(out) >= n:
                    break
    return out


def embed_paced(embedder, texts, input_type, max_tokens=8000, min_interval=21.0,
                on_batch=None):
    """Embed in token-bounded batches, spaced out, so it also works under
    Voyage's reduced limits (3 requests / 10K tokens per minute without a
    payment method). Tokens are estimated as len(text) / 3."""
    batches, cur, cur_tok = [], [], 0
    for t in texts:
        tok = len(t) // 3 + 1
        if cur and cur_tok + tok > max_tokens:
            batches.append(cur)
            cur, cur_tok = [], 0
        cur.append(t)
        cur_tok += tok
    if cur:
        batches.append(cur)
    out, last = [], 0.0
    for i, batch in enumerate(batches):
        for attempt in range(4):
            wait = min_interval - (time.perf_counter() - last)
            if last and wait > 0:
                time.sleep(wait)
            last = time.perf_counter()
            try:
                vec = embedder.embed(batch, input_type=input_type)
                out.append(vec)
                if on_batch:
                    on_batch(sum(len(b) for b in batches[:i]), vec)   # persist as we go
                break
            except RuntimeError as exc:
                if "429" not in str(exc) or attempt == 3:
                    raise
                time.sleep(60)   # per-minute window: wait it out
        print(f"  batch {i + 1}/{len(batches)} ({len(batch)} texts)")
    return np.vstack(out) if out else np.zeros((0, 0), dtype=np.float32)


def build_store(model: str, out_root: str, distractors: int = 0):
    src = _cfg.Config()
    papers = _index.load_papers(src)
    for pid, paper in load_distractors(distractors, out_root).items():
        papers.setdefault(pid, paper)   # never replace a corpus paper
    extracted = _index.load_extracted(src)
    chunks = []
    for pid, paper in papers.items():
        chunks.extend(_index.build_chunks(paper, extracted.get(pid)))

    dst = _cfg.Config()
    dst.local_storage_path = os.path.join(out_root, model)
    store = _store.VectorStore(dst)
    embedder = _emb.VoyageEmbedder(dst, model=model)
    todo = [c for c in chunks if c.chunk_id not in store.ids]
    if todo:
        t = time.perf_counter()
        embed_paced(embedder, [c.text for c in todo], "document",
                    on_batch=lambda off, vec: store.add(todo[off:off + len(vec)], vec,
                                                        model_name=model))
        print(f"[{model}] embedded {len(todo)} documents in {time.perf_counter() - t:.1f} s")
    return store, embedder, set(extracted)


def query_vectors(store, embedder, model: str, out_root: str) -> np.ndarray:
    rows = unit_rows(store)
    ids = [store.chunks[i].chunk_id for i in rows]
    cache = os.path.join(out_root, model, "queries.npz")
    if os.path.exists(cache):
        data = np.load(cache, allow_pickle=False)
        if list(data["ids"]) == ids:
            return data["vecs"]
    vecs = embed_paced(embedder, [store.chunks[i].text for i in rows], "query")
    np.savez(cache, ids=np.array(ids), vecs=vecs)
    return vecs


def evaluate(model: str, out_root: str, k: int = 5, distractors: int = 0) -> dict:
    store, embedder, extracted_ids = build_store(model, out_root, distractors)
    qv = query_vectors(store, embedder, model, out_root)
    all_papers = {c.paper_id for c in store.chunks if c.kind == "abstract"}
    small = all_papers & extracted_ids
    out = {"model": model}
    for name, pool in (("extracted_pool", small), ("full_pool", all_papers)):
        res = summarise(rank_source_papers(store, qv, pool), len(pool), k)
        res["task"] = "unit -> source paper (live query embeddings)"
        out[name] = res
    return out


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    _load_env()
    ap = argparse.ArgumentParser(prog="python -m evaluation.live")
    ap.add_argument("--model", action="append", required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--out", default=os.path.join("storage", "eval"))
    ap.add_argument("--distractors", type=int, default=0,
                    help="add N recent arXiv papers (fetched live, cached) to the candidate pool")
    ap.add_argument("--json", default=None, help="also write all results to this file")
    args = ap.parse_args()

    results = []
    for model in args.model:
        r = evaluate(model, args.out, args.k, args.distractors)
        results.append(r)
        for pool in ("extracted_pool", "full_pool"):
            s, b = r[pool], r[pool]["random_baseline"]
            print(f"{model:<15} {pool:<15} queries={s['queries']} candidates={s['candidates']:<4} "
                  f"R@1={s['recall@1']:.3f} R@{args.k}={s[f'recall@{args.k}']:.3f} "
                  f"MRR={s['mrr']:.3f}  (random R@{args.k}={b['recall_at_k']:.3f} MRR={b['mrr']:.3f})")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
