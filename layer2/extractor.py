"""LLM-based knowledge extraction: paper text in, validated scientific units out.

The flow for one paper (Extractor.extract):

    sections --chunk--> [prompt, ...] --LLM--> JSON --validate--> dataclasses
                                                 |  invalid
                                                 +--> retry once with the
                                                      validation error, then
                                                      skip with a warning

Design notes:
  * Extraction runs on an open model via the Hugging Face Inference API
    (huggingface_hub.InferenceClient). Inference providers don't uniformly
    support server-side structured outputs, so the JSON schema is embedded in
    the system prompt and every field is validated against the layer2.models
    dataclasses before anything is persisted -- the validation layer is the
    real guarantee that extracted.jsonl never contains junk.
  * 429/5xx retries are hand-rolled with exponential backoff, mirroring
    layer1/base_fetcher._get.
  * Long papers are chunked by section under a token budget; per-chunk unit
    lists are merged with light dedup (same claim found in two chunks -> one).
"""

import os
import re
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import httpx
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError, InferenceTimeoutError

from .config import Config
from .tei_parser import TeiSection
from .models import (
    ASSUMPTION_BASES, CLAIM_TYPES, CONFIDENCE_LEVELS, METHOD_ROLES,
    Assumption, Claim, DatasetRef, ExtractedPaper, Limitation, Method, Result,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt + schema
# ---------------------------------------------------------------------------

# The task prompt defines the extraction job once; the per-paper user turn
# carries only the paper text. The full SYSTEM_PROMPT (task + JSON schema) is
# assembled below, after EXTRACTION_SCHEMA is defined.
_TASK_PROMPT = """\
You are the Knowledge Extraction layer of a research-paper intelligence system.
Given one scientific paper (title, abstract, and possibly body sections), extract
machine-readable scientific units. Be faithful to the text: never invent units
that the paper does not support, and prefer fewer high-quality units over many
vague ones.

Extract these unit types:

1. claims - the paper's substantive scientific claims.
   - statement: one self-contained sentence (understandable without the paper).
   - claim_type: "empirical" (supported by experiments/measurements),
     "theoretical" (proofs, derivations, formal analysis), or
     "methodological" (about how to do something / a proposed technique).
   - evidence: a short snippet from the provided text that supports the claim.
   - confidence: "explicit" if the paper states the claim outright,
     "implied" if it follows from the text but is not stated directly.

2. methods - named techniques/architectures/algorithms.
   - role: "introduced" if the paper proposes it, "used" if pre-existing.

3. datasets - datasets used for training or evaluation (not ones merely cited).

4. results - key quantitative results: metric, value (verbatim, e.g. "85.3%"),
   plus the dataset and comparison baseline when stated. Skip results whose
   numeric value is not actually present in the provided text.

5. assumptions - preconditions the contribution relies on.
   - basis: "stated" if written down, "implied" if unstated but required.

6. limitations - limitations or failure modes, stated by the authors or
   clearly evident from the text.

For every unit, set "section" to the exact heading of the section it came from,
as given in the input ("Abstract" for the abstract)."""

# Reusable schema fragment: "string or null" (structured outputs require
# additionalProperties:false and explicit nullability via anyOf).
_NULLABLE_STR = {"anyOf": [{"type": "string"}, {"type": "null"}]}


def _unit_schema(props: Dict[str, dict]) -> dict:
    """Build the schema for one unit type: an object with exactly `props`
    (every unit also gets the provenance `section` field)."""
    props = {**props, "section": _NULLABLE_STR}
    return {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": list(props),
            "properties": props,
        },
    }


# JSON schema the model output is constrained to. Mirrors layer2.models 1:1
# (paper_id is absent on purpose -- we stamp it ourselves, the model never
# needs to know or repeat it).
EXTRACTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["claims", "methods", "datasets", "results",
                 "assumptions", "limitations"],
    "properties": {
        "claims": _unit_schema({
            "statement": {"type": "string"},
            "claim_type": {"type": "string", "enum": list(CLAIM_TYPES)},
            "evidence": {"type": "string"},
            "confidence": {"type": "string", "enum": list(CONFIDENCE_LEVELS)},
        }),
        "methods": _unit_schema({
            "name": {"type": "string"},
            "role": {"type": "string", "enum": list(METHOD_ROLES)},
            "description": {"type": "string"},
        }),
        "datasets": _unit_schema({
            "name": {"type": "string"},
            "purpose": {"type": "string"},
        }),
        "results": _unit_schema({
            "metric": {"type": "string"},
            "value": {"type": "string"},
            "dataset": _NULLABLE_STR,
            "baseline": _NULLABLE_STR,
        }),
        "assumptions": _unit_schema({
            "statement": {"type": "string"},
            "basis": {"type": "string", "enum": list(ASSUMPTION_BASES)},
        }),
        "limitations": _unit_schema({
            "statement": {"type": "string"},
        }),
    },
}

# Full system prompt = task description + the schema the response must match.
# The schema rides in the prompt (rather than a server-side response_format)
# because support for constrained decoding varies across HF inference
# providers; payload_to_units() below is the enforcement that actually counts.
SYSTEM_PROMPT = (
    _TASK_PROMPT
    + "\n\nYour entire response must be a single JSON object that validates "
      "against this JSON schema -- no markdown fences, no commentary, no text "
      "before or after the JSON:\n"
    + json.dumps(EXTRACTION_SCHEMA, indent=2)
)


def build_user_prompt(title: str, abstract: str,
                      sections: List[TeiSection],
                      chunk_info: str = "") -> str:
    """Assemble the per-paper (or per-chunk) user turn.

    Sections are rendered with `##`-marked headings so the model can attribute
    each unit to the right section verbatim.
    """
    parts = [f"# {title}".strip()]
    if chunk_info:
        # tells the model it is seeing a slice of a longer paper, so it does
        # not mistake a missing conclusion for the paper having none
        parts.append(f"(Note: {chunk_info})")
    if abstract:
        parts.append(f"## Abstract\n{abstract}")
    for sec in sections:
        parts.append(f"## {sec.heading}\n{sec.text}")
    if not abstract and not sections:
        parts.append("(No abstract or full text is available for this paper; "
                     "extract only what the title supports.)")
    parts.append("Extract the scientific units from the paper text above.")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Validation: JSON payload -> dataclasses
# ---------------------------------------------------------------------------

def _check(cond: bool, errors: List[str], msg: str) -> bool:
    """Tiny helper: record `msg` when `cond` fails. Returns cond so callers
    can skip a unit whose fields are unusable."""
    if not cond:
        errors.append(msg)
    return cond


def payload_to_units(payload: dict, paper_id: str) -> Dict[str, list]:
    """Validate a decoded JSON payload and build the unit dataclasses.

    Raises ValueError with *all* problems found (not just the first), so the
    retry prompt can show the model everything it got wrong in one shot.
    """
    if not isinstance(payload, dict):
        raise ValueError(f"top-level JSON must be an object, got {type(payload).__name__}")

    errors: List[str] = []
    units: Dict[str, list] = {key: [] for key in
                              ("claims", "methods", "datasets", "results",
                               "assumptions", "limitations")}

    def items(key: str) -> List[dict]:
        """The list under `key`, tolerating absence but not wrong types."""
        value = payload.get(key, [])
        if not isinstance(value, list):
            errors.append(f"'{key}' must be a list, got {type(value).__name__}")
            return []
        return [item for item in value
                if _check(isinstance(item, dict), errors,
                          f"every entry in '{key}' must be an object")]

    def text(item: dict, key: str, field_name: str, required: bool = True) -> str:
        """A string field; '' if absent. Records an error if required+empty."""
        value = item.get(field_name) or ""
        if not isinstance(value, str):
            errors.append(f"{key}.{field_name} must be a string")
            return ""
        value = value.strip()
        if required and not value:
            errors.append(f"{key}.{field_name} must be a non-empty string")
        return value

    def enum(item: dict, key: str, field_name: str, allowed: tuple) -> str:
        value = text(item, key, field_name)
        if value and value not in allowed:
            errors.append(f"{key}.{field_name} must be one of {allowed}, got '{value}'")
        return value

    def section(item: dict) -> Optional[str]:
        value = item.get("section")
        return value.strip() if isinstance(value, str) and value.strip() else None

    for it in items("claims"):
        units["claims"].append(Claim(
            paper_id=paper_id,
            statement=text(it, "claims", "statement"),
            claim_type=enum(it, "claims", "claim_type", CLAIM_TYPES),
            evidence=text(it, "claims", "evidence", required=False),
            confidence=enum(it, "claims", "confidence", CONFIDENCE_LEVELS),
            section=section(it)))
    for it in items("methods"):
        units["methods"].append(Method(
            paper_id=paper_id,
            name=text(it, "methods", "name"),
            role=enum(it, "methods", "role", METHOD_ROLES),
            description=text(it, "methods", "description", required=False),
            section=section(it)))
    for it in items("datasets"):
        units["datasets"].append(DatasetRef(
            paper_id=paper_id,
            name=text(it, "datasets", "name"),
            purpose=text(it, "datasets", "purpose", required=False),
            section=section(it)))
    for it in items("results"):
        dataset = it.get("dataset")
        baseline = it.get("baseline")
        units["results"].append(Result(
            paper_id=paper_id,
            metric=text(it, "results", "metric"),
            value=text(it, "results", "value"),
            dataset=dataset.strip() if isinstance(dataset, str) and dataset.strip() else None,
            baseline=baseline.strip() if isinstance(baseline, str) and baseline.strip() else None,
            section=section(it)))
    for it in items("assumptions"):
        units["assumptions"].append(Assumption(
            paper_id=paper_id,
            statement=text(it, "assumptions", "statement"),
            basis=enum(it, "assumptions", "basis", ASSUMPTION_BASES),
            section=section(it)))
    for it in items("limitations"):
        units["limitations"].append(Limitation(
            paper_id=paper_id,
            statement=text(it, "limitations", "statement"),
            section=section(it)))

    if errors:
        raise ValueError("; ".join(errors))
    return units


# ---------------------------------------------------------------------------
# The extractor itself
# ---------------------------------------------------------------------------

def _estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token). Only used for chunk budgeting,
    where being off by 20% is harmless."""
    return len(text) // 4 + 1


def _norm(text: str) -> str:
    """Normalization key for dedup across chunks: case/punctuation-insensitive."""
    return re.sub(r"\W+", "", text.lower())


def _strip_fences(text: str) -> str:
    """Open models often wrap JSON in markdown fences despite instructions;
    strip them so json.loads gets a fighting chance. Anything weirder than a
    fence still ends up in the validation-retry path, which is built for it."""
    text = text.strip()
    if text.startswith("```"):
        # drop the whole opening fence line ("```json", "```", ...)
        first_newline = text.find("\n")
        text = text[first_newline + 1:] if first_newline != -1 else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class Extractor:
    """Wraps the Hugging Face Inference API for the extract-one-paper operation."""

    def __init__(self, config: Config):
        self.config = config
        # HF_TOKEN is the standard env var huggingface_hub itself looks for;
        # HUGGINGFACEHUB_API_TOKEN is the legacy spelling some setups still use.
        token = (os.environ.get("HF_TOKEN")
                 or os.environ.get("HUGGINGFACEHUB_API_TOKEN"))
        if not token:
            raise RuntimeError(
                "HF_TOKEN is not set. Layer 2 calls the Hugging Face Inference "
                "API for extraction; create a token at "
                "https://huggingface.co/settings/tokens (needs the 'Make calls "
                "to Inference Providers' permission) and export it first, e.g.\n"
                "  PowerShell: $env:HF_TOKEN = 'hf_...'\n"
                "  bash:       export HF_TOKEN='hf_...'\n"
                "(or run with --dry-run to preview prompts without calling the API)")
        # provider="auto" routes to the first inference provider serving the
        # model; pin one via config.hf_provider when reproducibility matters.
        self.client = InferenceClient(provider=config.hf_provider, token=token)

    # --- chunking ----------------------------------------------------------

    def chunk_sections(self, sections: List[TeiSection]) -> List[List[TeiSection]]:
        """Greedily group sections under the per-call token budget.

        Most papers fit in a single chunk; this only kicks in for very long
        ones. A single oversized section still becomes its own chunk (we never
        split inside a section -- units need a section heading to point at).
        """
        budget = self.config.max_chunk_tokens
        chunks: List[List[TeiSection]] = []
        current: List[TeiSection] = []
        used = 0
        for sec in sections:
            cost = _estimate_tokens(sec.text)
            if current and used + cost > budget:
                chunks.append(current)
                current, used = [], 0
            current.append(sec)
            used += cost
        if current:
            chunks.append(current)
        return chunks or [[]]   # abstract-only papers -> one empty section list

    def build_prompts(self, title: str, abstract: str,
                      sections: List[TeiSection]) -> List[str]:
        """All user prompts for one paper (one per chunk). Public so the
        pipeline's --dry-run can print exactly what would be sent."""
        chunks = self.chunk_sections(sections)
        prompts = []
        for i, chunk in enumerate(chunks):
            info = (f"this is part {i + 1} of {len(chunks)} of the paper; "
                    f"other sections are processed separately"
                    if len(chunks) > 1 else "")
            # the abstract rides along with every chunk: it is short and gives
            # later chunks the global context they would otherwise lack
            prompts.append(build_user_prompt(title, abstract, chunk, info))
        return prompts

    # --- API call with 429/5xx backoff -------------------------------------

    def _call_api(self, user_prompt: str) -> str:
        """One chat-completion call; returns the (de-fenced) response text.

        Retries 429 and 5xx with exponential backoff (honouring Retry-After
        when the provider sends it), like layer1/base_fetcher._get. Other 4xx
        errors (bad model id, no provider access, ...) are bugs in *our*
        request and re-raise immediately.
        """
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.config.max_api_retries + 1):
            try:
                response = self.client.chat_completion(
                    model=self.config.model,
                    max_tokens=self.config.max_output_tokens,
                    # extraction wants faithful transcription, not creative
                    # sampling -- pin decoding down
                    temperature=0.0,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return _strip_fences(response.choices[0].message.content or "")
            except HfHubHTTPError as exc:
                status = exc.response.status_code if exc.response is not None else 0
                if status == 429:
                    # prefer the server's own Retry-After over our backoff
                    retry_after = exc.response.headers.get("retry-after", "")
                    wait = int(retry_after) if retry_after.isdigit() else 2 ** attempt
                    logger.warning("rate limited (attempt %d/%d), backing off %ds",
                                   attempt, self.config.max_api_retries, wait)
                elif status >= 500:
                    wait = 2 ** attempt
                    logger.warning("server error %d (attempt %d/%d), backing off %ds",
                                   status, attempt,
                                   self.config.max_api_retries, wait)
                else:
                    raise   # other 4xx won't heal by retrying
                last_exc = exc
            except (InferenceTimeoutError, httpx.HTTPError) as exc:
                # timeouts / connection drops: transient, worth retrying
                wait = 2 ** attempt
                logger.warning("connection error (attempt %d/%d): %s",
                               attempt, self.config.max_api_retries, exc)
                last_exc = exc
            time.sleep(wait)
        raise last_exc  # exhausted retries -- let the pipeline log + skip

    # --- call + validate (with the one validation retry) --------------------

    def _extract_chunk(self, paper_id: str, user_prompt: str) -> Optional[Dict[str, list]]:
        """Run one chunk through the model and validate; None means give up.

        On invalid JSON / failed validation we retry exactly once, appending
        the error to the prompt so the model can correct itself. After that we
        skip the chunk with a logged warning rather than fail the whole run.
        """
        prompt = user_prompt
        for attempt in range(self.config.max_validation_retries + 1):
            raw = self._call_api(prompt)
            try:
                return payload_to_units(json.loads(raw), paper_id)
            except (json.JSONDecodeError, ValueError) as exc:
                logger.warning("invalid extraction for %s (attempt %d): %s",
                               paper_id, attempt + 1, exc)
                # feed the validation error back so the retry can fix it
                prompt = (f"{user_prompt}\n\n"
                          f"Your previous response was rejected by the output "
                          f"validator with this error:\n  {exc}\n"
                          f"Produce corrected JSON that fixes every issue.")
        logger.warning("skipping chunk for %s: output still invalid after retry",
                       paper_id)
        return None

    # --- merging chunk results ------------------------------------------------

    @staticmethod
    def _merge_units(parts: List[Dict[str, list]]) -> Dict[str, list]:
        """Concatenate per-chunk unit lists, deduplicating across chunks.

        Chunks overlap on the abstract, so e.g. the headline claim tends to be
        extracted twice; dedup keys are per-type (a claim is its statement, a
        method its name, ...). For methods, "introduced" wins over "used" when
        the same name appears with both roles in different chunks.
        """
        keys = {
            "claims": lambda u: _norm(u.statement),
            "methods": lambda u: _norm(u.name),
            "datasets": lambda u: _norm(u.name),
            "results": lambda u: _norm(f"{u.metric}|{u.value}|{u.dataset or ''}"),
            "assumptions": lambda u: _norm(u.statement),
            "limitations": lambda u: _norm(u.statement),
        }
        merged: Dict[str, list] = {k: [] for k in keys}
        seen: Dict[str, Dict[str, object]] = {k: {} for k in keys}
        for part in parts:
            for kind, key_fn in keys.items():
                for unit in part.get(kind, []):
                    key = key_fn(unit)
                    if key in seen[kind]:
                        first = seen[kind][key]
                        if kind == "methods" and unit.role == "introduced":
                            first.role = "introduced"
                        continue
                    seen[kind][key] = unit
                    merged[kind].append(unit)
        return merged

    # --- public entry point ------------------------------------------------------

    def extract(self, paper_id: str, title: str, abstract: str,
                sections: List[TeiSection]) -> Optional[ExtractedPaper]:
        """Extract one paper. Returns None if every chunk failed validation."""
        prompts = self.build_prompts(title, abstract, sections)
        logger.info("extracting %s (%d chunk%s, %s)",
                    paper_id, len(prompts), "s" if len(prompts) > 1 else "",
                    "full text" if sections else "abstract only")

        parts = []
        for prompt in prompts:
            units = self._extract_chunk(paper_id, prompt)
            if units:
                parts.append(units)
        if not parts:
            logger.warning("no valid extraction produced for %s; skipping paper",
                           paper_id)
            return None

        merged = self._merge_units(parts)
        return ExtractedPaper(
            paper_id=paper_id,
            title=title,
            extraction_source="tei_full_text" if sections else "abstract_only",
            model=self.config.model,
            extracted_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **merged,
        )
