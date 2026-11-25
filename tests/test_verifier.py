"""Tests for the insight verifier, the analyst gate and the cross-paper fixes
(run: python -m unittest discover tests)."""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verifier import Corpus, check, check_all  # noqa: E402

CHUNKS = [
    {"chunk_id": "p1#abstract", "paper_id": "p1", "kind": "abstract", "text": "Paper one", "metadata": {}},
    {"chunk_id": "p1#claim:0", "paper_id": "p1", "kind": "claim", "text": "X improves Y.", "metadata": {}},
    {"chunk_id": "p1#claim:1", "paper_id": "p1", "kind": "claim", "text": "X costs more.", "metadata": {}},
    {"chunk_id": "p1#method:0", "paper_id": "p1", "kind": "method", "text": "Alpha: a method", "metadata": {"name": "Alpha"}},
    {"chunk_id": "p1#method:1", "paper_id": "p1", "kind": "method", "text": "Alpha-Lite: part of Alpha", "metadata": {"name": "Alpha-Lite"}},
    {"chunk_id": "p2#abstract", "paper_id": "p2", "kind": "abstract", "text": "Paper two", "metadata": {}},
    {"chunk_id": "p2#claim:0", "paper_id": "p2", "kind": "claim", "text": "X does not improve Y.", "metadata": {}},
    {"chunk_id": "p2#method:0", "paper_id": "p2", "kind": "method", "text": "Beta: another method", "metadata": {"name": "Beta"}},
]


def claim(cid, pid, text):
    return {"chunk_id": cid, "paper_id": pid, "statement": text}


def contradiction(a, b, iid="c1"):
    return {"id": iid, "kind": "contradiction", "provenance": [a["paper_id"], b["paper_id"]],
            "details": {"claim_a": a, "claim_b": b}}


class VerifierTest(unittest.TestCase):
    def setUp(self):
        self.corpus = Corpus.from_chunks(CHUNKS)

    def test_cross_paper_contradiction_passes(self):
        v = check(contradiction(claim("p1#claim:0", "p1", "X improves Y."),
                                claim("p2#claim:0", "p2", "X does not improve Y.")), self.corpus)
        self.assertTrue(v.passed, v.errors)

    def test_same_paper_contradiction_fails(self):
        v = check(contradiction(claim("p1#claim:0", "p1", "X improves Y."),
                                claim("p1#claim:1", "p1", "X costs more.")), self.corpus)
        self.assertFalse(v.passed)
        self.assertIn("same paper", v.errors[0])

    def test_misquoted_or_missing_claim_fails(self):
        v = check(contradiction(claim("p1#claim:0", "p1", "X improves Z a lot."),
                                claim("p9#claim:0", "p9", "nope")), self.corpus)
        self.assertTrue(any("differs" in e for e in v.errors))
        self.assertTrue(any("not in the corpus" in e for e in v.errors))

    def test_mirrored_duplicate_fails(self):
        a = claim("p1#claim:0", "p1", "X improves Y.")
        b = claim("p2#claim:0", "p2", "X does not improve Y.")
        verdicts = check_all([contradiction(a, b, "c1"), contradiction(b, a, "c2")], self.corpus)
        self.assertTrue(verdicts[0].passed)
        self.assertFalse(verdicts[1].passed)
        self.assertIn("duplicate", verdicts[1].errors[0])

    def test_synergy_rules(self):
        def syn(a, b):
            return {"id": "s", "kind": "synergy", "details": {
                "method_a": {"name": a, "paper_id": None}, "method_b": {"name": b, "paper_id": None}}}
        self.assertTrue(check(syn("Alpha", "Beta"), self.corpus).passed)
        same = check(syn("Alpha", "Alpha-Lite"), self.corpus)
        self.assertFalse(same.passed)
        self.assertIn("same paper", same.errors[0])
        self.assertFalse(check(syn("Alpha", "Gamma"), self.corpus).passed)

    def test_evidence_counts_and_verdict(self):
        ev = {"id": "e", "kind": "evidence",
              "summary": "Evidence on 'X': supported (2 supporting / 0 contradicting, from 3 claim(s))",
              "details": {"topic": "X", "verdict": "supported",
                          "supporting": [claim("p1#claim:0", "p1", "X improves Y.")],
                          "contradicting": [claim("p2#claim:0", "p2", "X does not improve Y.")]}}
        errs = check(ev, self.corpus).errors
        self.assertTrue(any("summary counts" in e for e in errs))
        self.assertTrue(any("verdict 'supported'" in e for e in errs))

    def test_hypothesis_grounding(self):
        good = {"id": "h", "kind": "hypothesis", "details": {"grounded_in": ["p1 (Alpha)", "p2 (Beta)"]}}
        bad = {"id": "h2", "kind": "hypothesis", "details": {"grounded_in": ["p1 (Beta)"]}}
        self.assertTrue(check(good, self.corpus).passed)
        self.assertFalse(check(bad, self.corpus).passed)

    def test_stub_is_a_warning_only(self):
        ins = contradiction(claim("p1#claim:0", "p1", "X improves Y."),
                            claim("p2#claim:0", "p2", "X does not improve Y."))
        ins["stub"] = True
        v = check(ins, self.corpus)
        self.assertTrue(v.passed)
        self.assertTrue(v.warnings)


class SpreadAcrossPapersTest(unittest.TestCase):
    def test_round_robin_keeps_rank_order(self):
        from layer4.tools import _spread_across_papers
        hits = [{"paper_id": p, "n": i} for i, p in enumerate(["a", "a", "a", "b", "c", "b"])]
        out = _spread_across_papers(hits, 4)
        self.assertEqual([h["paper_id"] for h in out], ["a", "b", "c", "a"])
        self.assertEqual(len(_spread_across_papers(hits, 10)), 6)


class AnalystGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        corpus_dir = os.path.join(self.tmp, "corpus")
        os.makedirs(corpus_dir)
        with open(os.path.join(corpus_dir, "chunks.jsonl"), "w", encoding="utf-8") as fh:
            for c in CHUNKS:
                fh.write(json.dumps(c) + "\n")
        from analyst.config import Config
        self.config = Config()
        self.config.local_storage_path = self.tmp
        self.config.corpus_storage_path = corpus_dir

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_gate_splits_banked_and_rejected(self):
        import analyst.engine as engine
        good = contradiction(claim("p1#claim:0", "p1", "X improves Y."),
                             claim("p2#claim:0", "p2", "X does not improve Y."), "good")
        bad = contradiction(claim("p1#claim:0", "p1", "X improves Y."),
                            claim("p1#claim:1", "p1", "X costs more."), "bad")

        from dataclasses import make_dataclass   # Finding stand-in (asdict needs a dataclass)
        Finding = make_dataclass("Finding", [(k, object) for k in good] + [("summary", str, ""),
                                 ("confidence", str, "high"), ("stub", bool, False)])
        orig = (engine.worklist.build_tasks, engine.worklist.graph_method_labels, engine.layer5.run_agent)
        try:
            Task = make_dataclass("Task", [("id", str), ("agent", str), ("topic", str)])
            engine.worklist.build_tasks = lambda *_: [Task("t1", "contradiction", "X")]
            engine.worklist.graph_method_labels = lambda: []
            engine.layer5.run_agent = lambda *a, **k: [Finding(**good), Finding(**bad)]
            eng = engine.AnalysisEngine(self.config, offline=True)
            summary = eng.tick(1, set(), set())
        finally:
            (engine.worklist.build_tasks, engine.worklist.graph_method_labels, engine.layer5.run_agent) = orig
        self.assertEqual((summary["new_insights"], summary["rejected"]), (1, 1))
        with open(self.config.rejected_path, encoding="utf-8") as fh:
            rej = [json.loads(l) for l in fh]
        self.assertEqual(rej[0]["id"], "bad")
        self.assertIn("same paper", rej[0]["_errors"][0])
        self.assertIn("bad", eng._known_insight_ids())   # rejected ids are not redone


if __name__ == "__main__":
    unittest.main()
