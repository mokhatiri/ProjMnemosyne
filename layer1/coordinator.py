"""
Fan-out coordinator: queries several sources concurrently, then deduplicates
and merges records that describe the same paper.

The sources don't share a query language (arXiv wants a search_query, S2 a
free-text query, OpenReview a venue id), so fetch_all takes a per-source map
{source_name: query}. Records are merged on DOI -> normalized arXiv id ->
title hash, so a paper appearing in several sources becomes one Paper that
combines their complementary fields (PDF, citations, review keywords, ...).
"""

import re
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

from .base_fetcher import BaseFetcher
from .models import Paper

logger = logging.getLogger(__name__)

# matches a bare arXiv id like 2401.01234 (ignoring any version suffix)
_ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})")


class FetchCoordinator:
    def __init__(self, fetchers: List[BaseFetcher], max_workers: int = 4):
        # index by source_name so callers can target queries per source
        self.fetchers = {f.source_name: f for f in fetchers}
        self.max_workers = max_workers

    def fetch_all(self, queries: Dict[str, str], **kwargs) -> List[Paper]:
        """`queries` maps source_name -> that source's query string. Only the
        named sources are queried. Runs them concurrently (I/O bound) and
        returns a deduplicated, merged list of Paper records."""
        targets = {name: q for name, q in queries.items() if name in self.fetchers}
        unknown = set(queries) - set(self.fetchers)
        if unknown:
            logger.warning("ignoring queries for unregistered sources: %s", unknown)

        results: List[Paper] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(self.fetchers[name].fetch, query, **kwargs): name
                for name, query in targets.items()
            }
            for fut in as_completed(futures):
                name = futures[fut]
                try:
                    results.extend(fut.result())
                except Exception:  # one bad source shouldn't sink the whole run
                    logger.exception("fetcher %s failed", name)

        return self._dedup_merge(results)

    @staticmethod
    def _identity_keys(paper: Paper) -> List[str]:
        """All identifiers this record exposes. Two records that share *any* of
        these refer to the same paper. A single record can carry several (e.g.
        an S2 paper with both a DOI and an external arXiv id), which is what lets
        us bridge records that each expose only one of them."""
        keys: List[str] = []
        if paper.doi:
            keys.append(f"doi:{paper.doi.lower()}")
        if paper.source == "arxiv":
            match = _ARXIV_ID.search(paper.source_id)
            if match:
                keys.append(f"arxiv:{match.group(1)}")
        arxiv_ext = (paper.extra.get("externalIds") or {}).get("ArXiv")
        if arxiv_ext:
            match = _ARXIV_ID.search(arxiv_ext)
            keys.append(f"arxiv:{match.group(1) if match else arxiv_ext}")
        # title is the always-available fallback so every record clusters somewhere
        norm_title = re.sub(r"\W+", "", paper.title.lower())
        keys.append("title:" + hashlib.sha1(norm_title.encode()).hexdigest())
        return keys

    def _dedup_merge(self, papers: List[Paper]) -> List[Paper]:
        """Cluster records that share any identifier, then merge each cluster.
        Uses a key -> cluster-representative map; when a new record bridges two
        existing clusters (shares a key with each) they are fused together."""
        clusters: Dict[int, Paper] = {}       # cluster id -> merged Paper
        key_to_cluster: Dict[str, int] = {}   # identifier -> cluster id
        next_id = 0

        for paper in papers:
            keys = self._identity_keys(paper)
            found = {key_to_cluster[k] for k in keys if k in key_to_cluster}

            if not found:
                cid = next_id
                next_id += 1
                clusters[cid] = paper
            else:
                # fuse all clusters this record touches into the lowest id
                cid = min(found)
                merged = clusters[cid]
                for other_id in found - {cid}:
                    merged = self._merge(merged, clusters.pop(other_id))
                merged = self._merge(merged, paper)
                clusters[cid] = merged

            # (re)point every key seen so far at the chosen cluster
            for k in [*keys, *self._identity_keys(clusters[cid])]:
                key_to_cluster[k] = cid

        return list(clusters.values())

    @staticmethod
    def _merge(base: Paper, other: Paper) -> Paper:
        """Combine two records of the same paper, preferring existing non-empty
        fields and unioning list fields. `base` keeps its source/id as canonical."""
        def pick(a, b):
            return a if a else b

        references = list(dict.fromkeys([*base.references, *other.references]))
        categories = list(dict.fromkeys([*base.categories, *other.categories]))
        authors = base.authors or other.authors
        extra = {**other.extra, **base.extra}
        # remember every source this paper was seen in
        extra.setdefault("also_seen_in", [])
        if other.source not in extra["also_seen_in"] and other.source != base.source:
            extra["also_seen_in"] = [*extra["also_seen_in"], other.source]

        return Paper(
            source=base.source+"/"+other.source if base.source != other.source else base.source,
            source_id=base.source_id+"/"+other.source_id if base.source_id != other.source_id else base.source_id,
            title=base.title,
            abstract=pick(base.abstract, other.abstract),
            authors=authors,
            categories=categories,
            published=pick(base.published, other.published),
            pdf_url=pick(base.pdf_url, other.pdf_url),
            doi=pick(base.doi, other.doi),
            references=references,
            extra=extra,
        )

    def get(self, source_name: str) -> Optional[BaseFetcher]:
        """Access an individual fetcher by source name."""
        return self.fetchers.get(source_name)
