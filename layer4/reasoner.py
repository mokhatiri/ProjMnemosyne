"""The LLM behind the two *reasoning* tools (detect_contradictions /
generate_hypotheses).

Layer 4's other tools are pure structured-data accessors over Layers 3-1/3-2.
These two need a model to actually judge text, so they delegate to a Reasoner.
Two implementations behind one interface:

  * HFReasoner -- the real thing. Calls the Hugging Face Inference API exactly
    like layer2/extractor.py (chat_completion, JSON output, 429/5xx backoff,
    HF_TOKEN from the env). This is what runs in production.
  * FakeReasoner -- a deterministic, clearly-labelled offline stub used when
    no HF_TOKEN is available (or `--offline` is passed). It does NOT reason; it
    returns a structured placeholder built from the inputs so the rest of the
    tool layer -- schemas, MCP wiring, retrieval grounding -- can be exercised
    end-to-end without a key. Every stub result is flagged ``"stub": true``.

Both expose the same two methods so tools.py never branches on which it holds:
    find_contradictions(topic, claims)   -> list[dict]
    propose_hypotheses(topic, grounding) -> list[dict]
"""

import os
import json
import time
import logging
from typing import Any, Dict, List, Optional

import httpx
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError, InferenceTimeoutError

from .config import Config

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    """Open models often wrap JSON in markdown fences; strip them before
    json.loads. (Same helper as layer2/extractor.py.)"""
    text = text.strip()
    if text.startswith("```"):
        nl = text.find("\n")
        text = text[nl + 1:] if nl != -1 else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ---------------------------------------------------------------------------
# Prompts (kept module-level + stable so they're easy to read and audit)
# ---------------------------------------------------------------------------

_CONTRADICTION_SYSTEM = """\
You are the contradiction-detection reasoner of a research-paper intelligence
system. You are given a topic and a numbered list of claims extracted from
different papers. Identify pairs of claims that genuinely CONTRADICT each other
-- where both cannot be true as stated, or they report opposing findings.

Be conservative: differing scope, different datasets, or merely different
emphasis are NOT contradictions. Only flag real tension. It is correct to
return an empty list when there is none.

Respond with JSON only, no prose, matching exactly:
{"contradictions": [
  {"claim_a": <int index>, "claim_b": <int index>,
   "explanation": "<why they conflict>", "confidence": "high"|"medium"|"low"}
]}"""

_HYPOTHESIS_SYSTEM = """\
You are the hypothesis-generation reasoner of a research-paper intelligence
system. Given a topic and structured grounding (claims, methods, and known
coverage gaps drawn from the corpus), propose novel but PLAUSIBLE research
hypotheses or directions. Each must be grounded in the supplied material --
reference the specific claims/methods/gaps it builds on. Do not invent results.

Respond with JSON only, no prose, matching exactly:
{"hypotheses": [
  {"hypothesis": "<one testable sentence>",
   "rationale": "<why it follows from the grounding>",
   "grounded_in": ["<short references to the claims/methods/gaps used>"]}
]}"""


class HFReasoner:
    """Real reasoning via the Hugging Face Inference API."""

    def __init__(self, config: Config):
        self.config = config
        token = (os.environ.get("HF_TOKEN")
                 or os.environ.get("HUGGINGFACEHUB_API_TOKEN"))
        if not token:
            raise RuntimeError(
                "HF_TOKEN is not set. Layer 4's reasoning tools "
                "(detect_contradictions / generate_hypotheses) call the Hugging "
                "Face Inference API; create a token at "
                "https://huggingface.co/settings/tokens (needs the 'Make calls "
                "to Inference Providers' permission) and export it, e.g.\n"
                "  PowerShell: $env:HF_TOKEN = 'hf_...'\n"
                "  bash:       export HF_TOKEN='hf_...'\n"
                "(or run the server / call with --offline to use the deterministic "
                "stub reasoner instead)")
        self.client = InferenceClient(provider=config.hf_provider, token=token)
        self.model_name = config.model

    # --- the one low-level call, with 429/5xx backoff (the Layer 1/2 pattern) --
    def _complete_json(self, system: str, user: str) -> dict:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.config.max_api_retries + 1):
            try:
                resp = self.client.chat_completion(
                    model=self.config.model,
                    max_tokens=self.config.max_output_tokens,
                    temperature=0.0,        # judgement, not creativity
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}],
                )
                raw = _strip_fences(resp.choices[0].message.content or "")
                return json.loads(raw)
            except json.JSONDecodeError as exc:
                # malformed JSON is not retryable in a useful way here -- the
                # caller treats an empty result as "model produced nothing usable"
                logger.warning("reasoner returned non-JSON: %s", exc)
                return {}
            except HfHubHTTPError as exc:
                status = exc.response.status_code if exc.response is not None else 0
                if status == 429:
                    retry_after = exc.response.headers.get("retry-after", "")
                    wait = int(retry_after) if retry_after.isdigit() else 2 ** attempt
                elif status >= 500:
                    wait = 2 ** attempt
                else:
                    raise   # 4xx other than 429 won't heal
                logger.warning("HF API %d (attempt %d/%d), backing off %ds",
                               status, attempt, self.config.max_api_retries, wait)
                last_exc = exc
            except (InferenceTimeoutError, httpx.HTTPError) as exc:
                wait = 2 ** attempt
                logger.warning("connection error (attempt %d/%d): %s",
                               attempt, self.config.max_api_retries, exc)
                last_exc = exc
            time.sleep(wait)
        raise last_exc

    def find_contradictions(self, topic: str,
                            claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ask the model which of ``claims`` contradict each other."""
        listing = "\n".join(
            f"[{i}] ({c.get('paper_id')}) {c.get('statement')}"
            for i, c in enumerate(claims))
        user = f"Topic: {topic}\n\nClaims:\n{listing}"
        data = self._complete_json(_CONTRADICTION_SYSTEM, user)
        out = []
        for item in data.get("contradictions", []):
            a, b = item.get("claim_a"), item.get("claim_b")
            if not (isinstance(a, int) and isinstance(b, int)):
                continue
            if not (0 <= a < len(claims) and 0 <= b < len(claims)) or a == b:
                continue
            out.append({
                "claim_a": claims[a], "claim_b": claims[b],
                "explanation": item.get("explanation", ""),
                "confidence": item.get("confidence", "low"),
            })
        return out

    def propose_hypotheses(self, topic: str,
                           grounding: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ask the model for grounded hypotheses given the assembled context."""
        user = (f"Topic: {topic}\n\nGrounding (JSON):\n"
                f"{json.dumps(grounding, ensure_ascii=False, indent=2)}")
        data = self._complete_json(_HYPOTHESIS_SYSTEM, user)
        out = []
        for item in data.get("hypotheses", []):
            stmt = (item.get("hypothesis") or "").strip()
            if stmt:
                out.append({"hypothesis": stmt,
                            "rationale": item.get("rationale", ""),
                            "grounded_in": item.get("grounded_in", [])})
        return out


class FakeReasoner:
    """Deterministic offline stub. Returns structured placeholders, never real
    reasoning -- so the tool layer is runnable without an HF_TOKEN. Every result
    is flagged ``stub: true`` so no caller mistakes it for a model judgement."""

    model_name = "offline-stub"

    def __init__(self, config: Optional[Config] = None):
        self.config = config

    def find_contradictions(self, topic: str,
                            claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # We can't actually judge contradiction offline. Surface the two claims
        # from *different* papers as a candidate pair so the shape is real, and
        # flag it loudly as a stub.
        cross = _first_cross_paper_pair(claims)
        if not cross:
            return []
        a, b = cross
        return [{
            "claim_a": a, "claim_b": b,
            "explanation": "OFFLINE STUB: real contradiction judgement needs "
                           "HF_TOKEN. These two cross-paper claims on the topic "
                           "are surfaced as a candidate only.",
            "confidence": "low", "stub": True,
        }]

    def propose_hypotheses(self, topic: str,
                           grounding: Dict[str, Any]) -> List[Dict[str, Any]]:
        methods = [m.get("text") or m.get("name") for m in grounding.get("methods", [])][:2]
        gaps = grounding.get("coverage_gaps", [])[:1]
        hyps = []
        if len(methods) >= 2:
            hyps.append({
                "hypothesis": f"Combining {methods[0]} and {methods[1]} may "
                              f"improve results on '{topic}'.",
                "rationale": "OFFLINE STUB: templated from the two methods most "
                             "associated with the topic; not a model judgement.",
                "grounded_in": methods, "stub": True})
        if gaps:
            g = gaps[0]
            hyps.append({
                "hypothesis": f"Evaluating {g.get('method')} on "
                              f"{g.get('missing_dataset')} would close a coverage gap.",
                "rationale": "OFFLINE STUB: templated from a knowledge-graph "
                             "coverage gap; not a model judgement.",
                "grounded_in": [f"gap: {g.get('method')} vs {g.get('missing_dataset')}"],
                "stub": True})
        return hyps


def _first_cross_paper_pair(claims: List[Dict[str, Any]]):
    """First pair of claims that come from two different papers (or None)."""
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            if claims[i].get("paper_id") != claims[j].get("paper_id"):
                return claims[i], claims[j]
    return None


def get_reasoner(config: Config, offline: bool = False):
    """Pick a reasoner. Explicit ``offline`` forces the stub; otherwise use the
    real HF reasoner, but fall back to the stub (with a warning) when no token
    is configured so the tools degrade instead of hard-failing."""
    if offline:
        return FakeReasoner(config)
    try:
        return HFReasoner(config)
    except RuntimeError as exc:
        logger.warning("%s\n-> falling back to the offline stub reasoner.", exc)
        return FakeReasoner(config)
