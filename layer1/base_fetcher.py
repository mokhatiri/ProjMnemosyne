"""
Abstract base for all paper sources.

BaseFetcher owns everything common (HTTP session with retry/backoff,
metadata/PDF storage, GROBID extraction, the per-paper ingest pipeline).
Each source is a concrete subclass that only implements fetch().
"""

import os
import json
import time
import hashlib
import tempfile
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import List, Optional

import requests

from .config import Config
from .models import Paper

# logger is set up at the module level so it can be used in both the base class and
# concrete fetchers; it will inherit the configuration from the main script when run.
logger = logging.getLogger(__name__)


# abstract base: everything common to every source lives here
# ABC : abstract base class from the abc module
class BaseFetcher(ABC):
    #: subclasses set this; used as Paper.source and for logging
    source_name: str = "base"

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session() # for faster HTTP and shared headers
        self.session.headers.update({"User-Agent": config.user_agent})
        os.makedirs(config.local_storage_path, exist_ok=True) # ensure storage dir exists

    # --- the one thing every source must implement ---
    @abstractmethod
    def fetch(self, query: str, **kwargs) -> List[Paper]:
        """Query the source and return normalized Paper records."""
        raise NotImplementedError

    # --- low-level HTTP with retry/backoff ---
    def _get(self, url: str, **kwargs) -> Optional[requests.Response]:
        print("----------------------------------------") # separator for readability in logs
        print("getting URL:", url, "...") # log the URL being fetched
        kwargs.setdefault("timeout", self.config.request_timeout) # default timeout for all requests

        # we keep attemting till max_retries, with incremental backoff for rate limits and server errors
        for attempt in range(1, self.config.max_retries + 1):
            try:
                resp = self.session.get(url, **kwargs) # passed
                print("got response with status code:", resp.status_code) # log the status code of the response
            except requests.RequestException as exc: # exceptions from requests

                logger.warning("GET %s failed (attempt %d): %s", url, attempt, exc) # put a warning in the logs with the URL, attempt number and exception message
                time.sleep(2 ** attempt) # incremental backoff: 2s, 4s, 8s, ...
                continue

            if resp.status_code == 429 or resp.status_code >= 500: # handle rate limits and server errors with backoff
                wait = int(resp.headers.get("Retry-After", 2 ** attempt)) # use Retry-After header if provided, otherwise exponential backoff
                logger.warning("GET %s -> %d, backing off %ds", url, resp.status_code, wait) # log the status code and backoff time
                time.sleep(wait)
                continue

            if resp.ok:
                print("successfully fetched URL:", url) # log successful fetches
                print("----------------------------------------") # separator for readability in logs
                return resp # return on success

            print(f"GET {url} -> {resp.status_code}: {resp.text[:200]}") # log other HTTP errors with status code and response snippet
            logger.error("GET %s -> %d: %s", url, resp.status_code, resp.text[:200]) # log other HTTP errors with status code and response snippet
            print("----------------------------------------") # separator for readability in logs
            return None # for non-retryable errors we return None immediately

        print(f"failed to GET URL after {self.config.max_retries} attempts: {url}") # log the final failure after exhausting retries
        print("----------------------------------------") # separator for readability in logs
        return None # after exhausting retries we return None

    # --- storage ---
    def store_metadata(self, paper: Paper) -> None:
        """Append-only JSONL sink. Swap for a Postgres upsert in production;
        keep the interface (one Paper in) identical so callers don't change."""
        print("----------------------------------------") # separator for readability in logs
        print("storing metadata for paper:", paper.paper_id) # log the paper ID being stored
        path = os.path.join(self.config.local_storage_path, "metadata.jsonl")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(paper), ensure_ascii=False) + "\n")
        print("successfully stored metadata for paper:", paper.paper_id) # log successful storage
        print("----------------------------------------") # separator for readability in logs

    def store_pdf(self, pdf_url: str) -> Optional[str]:
        """Download a PDF to a temp file and return the local path. Caller is
        responsible for deleting it after extraction (see ingest())."""
        print("----------------------------------------") # separator for readability in logs
        print("storing PDF from URL:", pdf_url) # log the PDF URL being stored
        resp = self._get(pdf_url, stream=True)
        if resp is None:
            print("failed to fetch PDF from URL:", pdf_url) # log the failure to fetch the PDF
            print("----------------------------------------") # separator for readability in logs
            return None
        fd, tmp_path = tempfile.mkstemp(suffix=".pdf",
                                        dir=self.config.local_storage_path)
        with os.fdopen(fd, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                fh.write(chunk)
        print("successfully stored PDF to path:", tmp_path) # log the local path where the PDF was stored
        print("----------------------------------------") # separator for readability in logs
        return tmp_path

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Send the PDF to GROBID and return TEI XML (structured full text)."""
        print("----------------------------------------") # separator for readability in logs
        print("extracting text from PDF at path:", pdf_path) # log the PDF path
        try:
            with open(pdf_path, "rb") as fh:
                resp = self.session.post(
                    self.config.grobid_endpoint,
                    files={"input": fh},
                    data={"consolidateHeader": "1", "segmentSentences": "1"},
                    timeout=self.config.request_timeout * 4,  # GROBID is slow on big PDFs
                )
        except requests.RequestException as exc:
            # GROBID is an optional external service; if it's unreachable, treat it
            # like a failed extraction rather than crashing the whole ingest run.
            logger.warning("GROBID unreachable at %s: %s", self.config.grobid_endpoint, exc)
            print("GROBID unreachable, skipping extraction:", exc)
            print("----------------------------------------")
            return ""
        if not resp.ok:
            print("failed to extract text from PDF at path:", pdf_path) # log the failure to extract text
            print("----------------------------------------") # separator for readability in logs
            return ""
        print("successfully extracted text from PDF at path:", pdf_path) # log the successful extraction
        print("----------------------------------------") # separator for readability in logs
        return resp.text

    # --- end-to-end per-paper pipeline (shared) ---
    def ingest(self, paper: Paper) -> Paper:
        """Fetch PDF -> extract text via GROBID -> discard PDF, keeping only the
        URL for on-demand re-fetch. Stores TEI XML alongside metadata."""
        print("----------------------------------------") # separator for readability in logs
        print("ingesting paper:", paper.paper_id) # log the paper ID being ingested
        if paper.pdf_url:
            pdf_path = self.store_pdf(paper.pdf_url)
            if pdf_path:
                try:
                    tei = self.extract_text_from_pdf(pdf_path)
                    if tei:
                        key = hashlib.sha1(paper.paper_id.encode()).hexdigest()
                        tei_path = os.path.join(self.config.local_storage_path,
                                                f"{key}.tei.xml")
                        with open(tei_path, "w", encoding="utf-8") as fh:
                            fh.write(tei)
                        paper.extra["tei_path"] = tei_path
                        print("successfully ingested paper with TEI XML:", paper.paper_id) # log successful ingestion with TEI XML
                    else:
                        print("ingested paper without TEI XML due to extraction failure:", paper.paper_id) # log ingestion without TEI XML due to extraction failure
                finally:
                    os.remove(pdf_path)  # discard PDF to save storage
                    print("discarded PDF at path:", pdf_path) # log the discarding of the PDF
            else:
                print("ingested paper without PDF due to download failure:", paper.paper_id) # log ingestion without PDF due to download failure
        self.store_metadata(paper)
        print("successfully ingested paper metadata:", paper.paper_id) # log successful ingestion of metadata   
        print("----------------------------------------") # separator for readability in logs
        return paper
