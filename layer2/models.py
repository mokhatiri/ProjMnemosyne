"""Structured representations of what Layer 2 extracts from a paper.

Mirrors the style of layer1/models.py: plain dataclasses, no framework.

Layer 1 ends with a Paper (title, abstract, maybe TEI full text). Layer 2 turns
that into machine-readable *scientific units* (ref.md §3.2): claims, methods,
datasets, results, assumptions, limitations. Each unit type carries:

  * the owning ``paper_id``  -- so Layers 3 (embedding/RAG) and 4 (knowledge
    graph) can index units individually and still trace them back, and
  * the ``section`` heading it was extracted from (None when the unit came
    from an abstract-only paper) -- provenance inside the paper itself.
"""

from dataclasses import dataclass, field
from typing import List, Optional

# Allowed values for the enum-ish string fields below. The LLM is told these
# via the JSON schema in the prompt (extractor.py) and we re-check them when
# validating the response, so bad values can never reach extracted.jsonl.
CLAIM_TYPES = ("empirical", "theoretical", "methodological")
CONFIDENCE_LEVELS = ("explicit", "implied")
METHOD_ROLES = ("introduced", "used")
ASSUMPTION_BASES = ("stated", "implied")


@dataclass
class Claim:
    """A single scientific claim the paper makes."""
    paper_id: str
    statement: str                  # the claim itself, as one self-contained sentence
    claim_type: str                 # "empirical" | "theoretical" | "methodological"
    evidence: str = ""              # short supporting snippet from the paper text
    confidence: str = "explicit"    # "explicit" (stated outright) | "implied" (inferred)
    section: Optional[str] = None   # TEI section heading the claim came from


@dataclass
class Method:
    """A named technique/architecture/algorithm the paper introduces or uses."""
    paper_id: str
    name: str                       # canonical name, e.g. "Target-SFT", "LoRA"
    role: str                       # "introduced" (novel here) | "used" (pre-existing)
    description: str = ""           # one-line description of what it is / does
    section: Optional[str] = None


@dataclass
class DatasetRef:
    """A dataset the paper uses for training or evaluation.

    Named DatasetRef (not Dataset) to avoid colliding with the many `Dataset`
    classes in the ML ecosystem and to signal this is a *reference* to one.
    """
    paper_id: str
    name: str                       # e.g. "GSM8K", "ImageNet"
    purpose: str = ""               # how the paper uses it (evaluation, training, ...)
    section: Optional[str] = None


@dataclass
class Result:
    """A key quantitative result reported by the paper."""
    paper_id: str
    metric: str                     # e.g. "accuracy", "BLEU", "Average@16"
    value: str                      # kept as a string: "85.3%", "0.42", "2x speedup"
    dataset: Optional[str] = None   # dataset the number was measured on, if stated
    baseline: Optional[str] = None  # what it is compared against, if stated
    section: Optional[str] = None


@dataclass
class Assumption:
    """A precondition the paper's contribution relies on."""
    paper_id: str
    statement: str
    basis: str = "stated"           # "stated" (written down) | "implied" (unstated but required)
    section: Optional[str] = None


@dataclass
class Limitation:
    """A limitation / failure mode, stated by the authors or clearly evident."""
    paper_id: str
    statement: str
    section: Optional[str] = None


@dataclass
class ExtractedPaper:
    """Everything Layer 2 extracted from one paper -- one line of extracted.jsonl.

    ``extraction_source`` records whether the units were mined from the GROBID
    full text or only from title+abstract, because downstream layers should
    weigh abstract-only extractions as less complete. ``model`` records which
    LLM produced the units, for reproducibility/auditing.
    """
    paper_id: str
    title: str
    extraction_source: str          # "tei_full_text" | "abstract_only"
    model: str                      # model id that did the extraction
    extracted_at: str               # ISO timestamp of the extraction run
    claims: List[Claim] = field(default_factory=list)
    methods: List[Method] = field(default_factory=list)
    datasets: List[DatasetRef] = field(default_factory=list)
    results: List[Result] = field(default_factory=list)
    assumptions: List[Assumption] = field(default_factory=list)
    limitations: List[Limitation] = field(default_factory=list)

    def unit_count(self) -> int:
        """Total number of extracted units, handy for logging/summaries."""
        return (len(self.claims) + len(self.methods) + len(self.datasets)
                + len(self.results) + len(self.assumptions) + len(self.limitations))
