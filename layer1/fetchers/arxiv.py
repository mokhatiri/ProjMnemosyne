"""arXiv source: queries the public Atom API and maps entries to Paper records."""

import time
import xml.etree.ElementTree as ET
from typing import List

from ..base_fetcher import BaseFetcher
from ..models import Paper


class ArxivFetcher(BaseFetcher):
    source_name = "arxiv"

    def fetch(self, query: str, max_results: int = 50, start: int = 0,
              **kwargs) -> List[Paper]:
        """`query` is an arXiv search_query, e.g. 'cat:cs.AI AND abs:transformer'."""
        ns = {"atom": "http://www.w3.org/2005/Atom",
              "arxiv": "http://arxiv.org/schemas/atom"}
        resp = self._get(self.config.arxiv_api_endpoint, params={
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        })
        if resp is None:
            return []

        papers: List[Paper] = []
        root = ET.fromstring(resp.text)
        for entry in root.findall("atom:entry", ns):
            arxiv_url = entry.findtext("atom:id", default="", namespaces=ns)
            arxiv_id = arxiv_url.rsplit("/abs/", 1)[-1]  # e.g. 2401.01234v1

            pdf_url = None
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href")

            authors = [a.findtext("atom:name", default="", namespaces=ns)
                       for a in entry.findall("atom:author", ns)]
            categories = [c.get("term") for c in entry.findall("atom:category", ns)
                          if c.get("term")]

            papers.append(Paper(
                source=self.source_name,
                source_id=arxiv_id,
                title=" ".join(entry.findtext("atom:title", "", ns).split()),
                abstract=" ".join(entry.findtext("atom:summary", "", ns).split()),
                authors=[a for a in authors if a],
                categories=categories,
                published=entry.findtext("atom:published", None, ns),
                pdf_url=pdf_url,
                doi=entry.findtext("arxiv:doi", None, ns),
            ))
        # arXiv asks for >= 3s between programmatic requests.
        time.sleep(3)
        return papers
