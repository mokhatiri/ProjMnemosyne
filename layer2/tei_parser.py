"""Parse GROBID TEI XML into clean, prompt-ready sections.

Layer 1 stores full text as TEI XML (storage/<sha1>.tei.xml). TEI is verbose --
namespaced XML with per-sentence <s> tags, inline <ref> citations, formulas,
author affiliations, etc. The LLM extractor only needs *clean text grouped by
section*, so this module flattens TEI into a small TeiDocument:

    title / abstract / [(heading, text), ...] / [reference titles]

Deliberately stdlib-only (xml.etree.ElementTree) -- no lxml, no new heavy
dependencies. Anything that can go wrong (missing file, malformed XML, missing
elements) returns None / empty values instead of raising, so the pipeline can
always fall back to abstract-only extraction.
"""

import os
import re
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)

# Every element in GROBID output lives in the TEI namespace; ElementTree
# requires it to be spelled out in find()/findall() paths.
TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}


@dataclass
class TeiSection:
    """One body section: its heading and the flattened paragraph text."""
    heading: str    # e.g. "1 Introduction" (number prefix kept when present)
    text: str


@dataclass
class TeiDocument:
    """The cleaned-up content of one TEI file."""
    title: str = ""
    abstract: str = ""
    sections: List[TeiSection] = field(default_factory=list)
    # Bibliography entry titles. Not sent to the LLM (they would bloat the
    # prompt without adding extractable units) but parsed here because Layer 4
    # (knowledge graph) will want them for citation edges.
    references: List[str] = field(default_factory=list)


def _clean(text: str) -> str:
    """Collapse runs of whitespace. TEI is pretty-printed, so raw itertext()
    output is littered with newlines and indentation."""
    return re.sub(r"\s+", " ", text).strip()


def _element_text(elem: Optional[ET.Element]) -> str:
    """All text inside an element, inline children (refs, formulas) included."""
    if elem is None:
        return ""
    return _clean("".join(elem.itertext()))


def _section_from_div(div: ET.Element) -> Optional[TeiSection]:
    """Turn one <div> of the TEI body into a TeiSection.

    GROBID emits one <div> per detected section with an optional <head>
    (heading, with the section number in an ``n`` attribute) followed by
    <p>/<formula>/<note> children. We keep everything except the heading
    element itself as the section text.
    """
    head = div.find("tei:head", TEI_NS)
    heading = _element_text(head)
    if head is not None and head.get("n"):
        # keep the section number ("1", "4.2", ...) so headings stay unique
        heading = f"{head.get('n')} {heading}".strip()

    # join the text of every child except the heading
    parts = []
    for child in div:
        if child is head:
            continue
        text = _element_text(child)
        if text:
            parts.append(text)
    body = " ".join(parts)

    if not body:
        return None  # empty divs (figure containers etc.) are useless to the LLM
    return TeiSection(heading=heading or "(untitled section)", text=body)


def parse_tei_file(path: str) -> Optional[TeiDocument]:
    """Parse one TEI file; return None if it is missing or malformed.

    Returning None (instead of raising) is the contract that lets the pipeline
    degrade gracefully to abstract-only extraction for that paper.
    """
    if not path or not os.path.exists(path):
        logger.warning("TEI file not found: %s", path)
        return None
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        logger.warning("TEI file %s is malformed XML: %s", path, exc)
        return None

    root = tree.getroot()
    doc = TeiDocument()

    # --- header: title + abstract -------------------------------------------
    doc.title = _element_text(
        root.find(".//tei:teiHeader//tei:titleStmt/tei:title", TEI_NS))
    doc.abstract = _element_text(
        root.find(".//tei:teiHeader//tei:profileDesc/tei:abstract", TEI_NS))

    # --- body sections --------------------------------------------------------
    for div in root.findall(".//tei:text/tei:body/tei:div", TEI_NS):
        section = _section_from_div(div)
        if section:
            doc.sections.append(section)

    # --- bibliography (titles only, for Layer 4) ------------------------------
    for bibl in root.findall(".//tei:back//tei:listBibl/tei:biblStruct", TEI_NS):
        title = _element_text(bibl.find(".//tei:title", TEI_NS))
        if title:
            doc.references.append(title)

    if not doc.sections and not doc.abstract:
        # parsed fine but contained nothing usable -- treat like a parse failure
        logger.warning("TEI file %s has no abstract or body sections", path)
        return None
    return doc
