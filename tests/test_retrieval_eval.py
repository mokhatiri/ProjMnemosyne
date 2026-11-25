"""Tests for the offline retrieval evaluation (run: python -m unittest discover tests)."""

import importlib
import os
import shutil
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.metrics import mean_reciprocal_rank, random_baseline, recall_at_k  # noqa: E402
from evaluation.retrieval import rank_source_papers, run, summarise  # noqa: E402

_models = importlib.import_module("layer3-1.models")
_config = importlib.import_module("layer3-1.config")
_store = importlib.import_module("layer3-1.store")


class MetricsTest(unittest.TestCase):
    def test_recall_at_k(self):
        ranks = [1, 2, 6, None]
        self.assertAlmostEqual(recall_at_k(ranks, 1), 0.25)
        self.assertAlmostEqual(recall_at_k(ranks, 5), 0.5)
        self.assertAlmostEqual(recall_at_k(ranks, 10), 0.75)

    def test_mrr(self):
        self.assertAlmostEqual(mean_reciprocal_rank([1, 2, 4, None]), (1 + 0.5 + 0.25) / 4)

    def test_empty(self):
        self.assertEqual(recall_at_k([], 5), 0.0)
        self.assertEqual(mean_reciprocal_rank([]), 0.0)

    def test_random_baseline(self):
        base = random_baseline(4, 2)
        self.assertAlmostEqual(base["recall_at_k"], 0.5)
        self.assertAlmostEqual(base["mrr"], (1 + 1 / 2 + 1 / 3 + 1 / 4) / 4)


class EndToEndTest(unittest.TestCase):
    """Three papers in three orthogonal directions; one unit per paper points
    at its own paper, one deliberately points at another paper."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        cfg = _config.Config()
        cfg.local_storage_path = self.tmp
        store = _store.VectorStore(cfg)
        Chunk = _models.Chunk
        chunks, vecs = [], []
        for i, pid in enumerate(["p0", "p1", "p2"]):
            e = np.zeros(3, dtype=np.float32)
            e[i] = 1.0
            chunks.append(Chunk(f"{pid}#abstract", pid, "abstract", f"paper {i}"))
            vecs.append(e)
            chunks.append(Chunk(f"{pid}#claim:0", pid, "claim", f"claim of {i}"))
            vecs.append(e + 0.1)
        # p0's method sits right on p2's direction: its paper should rank 2nd or 3rd
        chunks.append(Chunk("p0#method:0", "p0", "method", "misleading method"))
        vecs.append(np.array([0.2, 0.0, 1.0], dtype=np.float32))
        store.add(chunks, np.stack(vecs), model_name="fake-hash-test")
        self.cfg = cfg
        self.store = store

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ranks(self):
        recs = {r["chunk_id"]: r["rank"] for r in rank_source_papers(self.store)}
        self.assertEqual(recs["p0#claim:0"], 1)
        self.assertEqual(recs["p1#claim:0"], 1)
        self.assertEqual(recs["p2#claim:0"], 1)
        self.assertEqual(recs["p0#method:0"], 2)
        self.assertNotIn("p0#abstract", recs)  # abstracts are candidates, not queries

    def test_pool_and_query_vectors(self):
        # pool without p2: p0's misleading method now finds p0 first among {p0, p1}
        recs = {r["chunk_id"]: r["rank"]
                for r in rank_source_papers(self.store, pool={"p0", "p1"})}
        self.assertEqual(recs["p0#method:0"], 1)
        self.assertNotIn("p2#claim:0", recs)  # queries from outside the pool are skipped
        # explicit query vectors replace the stored ones (one per unit row)
        from evaluation.retrieval import unit_rows
        qv = np.tile(np.array([0, 1, 0], dtype=np.float32), (len(unit_rows(self.store)), 1))
        recs = {r["chunk_id"]: r["rank"]
                for r in rank_source_papers(self.store, query_vectors=qv)}
        self.assertEqual(recs["p1#claim:0"], 1)
        self.assertNotEqual(recs["p0#claim:0"], 1)

    def test_summary_and_run(self):
        res = summarise(rank_source_papers(self.store), n_papers=3, k=1)
        self.assertEqual(res["queries"], 4)
        self.assertAlmostEqual(res["recall@1"], 0.75)
        self.assertAlmostEqual(res["mrr"], (1 + 1 + 1 + 0.5) / 4)
        full = run(self.tmp, k=5)
        self.assertEqual(full["candidates"], 3)
        self.assertEqual(full["model"], "fake-hash-test")


if __name__ == "__main__":
    unittest.main()
