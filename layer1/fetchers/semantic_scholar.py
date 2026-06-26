"""Semantic Scholar source: S2 Graph API paper search mapped to Paper records."""

from typing import List

from ..config import Config
from ..base_fetcher import BaseFetcher
from ..models import Paper


class SemanticScholarFetcher(BaseFetcher):
    source_name = "semantic_scholar"

    # additional attribute : api key
    def __init__(self, config: Config):
        super().__init__(config)
        # Optional key raises the rate limit; absent -> shared anonymous pool.
        # the testing was done without a key, so the fetcher works fine without it, but if you have one you can set it in the config or env vars to speed things up.
        api_key = getattr(config, "semantic_scholar_api_key", None)
        if api_key:
            self.session.headers.update({"x-api-key": api_key})

    def fetch(self, query: str, limit: int = 50, **kwargs) -> List[Paper]:
        fields = "title,abstract,authors,year,externalIds,openAccessPdf,fieldsOfStudy,references.paperId"
        resp = self._get(f"{self.config.semantic_scholar_api_endpoint}/paper/search",
                         params={"query": query, "limit": limit, "fields": fields})
        if resp is None:
            return []

        papers: List[Paper] = []
        for item in resp.json().get("data", []):
            ext = item.get("externalIds") or {}
            oa = item.get("openAccessPdf") or {}
            papers.append(Paper(
                source=self.source_name,
                source_id=item["paperId"],
                title=item.get("title") or "",
                abstract=item.get("abstract") or "",
                authors=[a.get("name", "") for a in item.get("authors") or []],
                categories=item.get("fieldsOfStudy") or [],
                published=str(item["year"]) if item.get("year") else None,
                pdf_url=oa.get("url"),
                doi=ext.get("DOI"),
                references=[r["paperId"] for r in item.get("references") or []
                            if r.get("paperId")],
                extra={"externalIds": ext},
            ))
        return papers
