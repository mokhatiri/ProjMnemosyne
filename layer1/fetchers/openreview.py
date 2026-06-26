"""OpenReview source: API v2 notes for a venue mapped to Paper records."""

from typing import List, Dict, Any

from ..base_fetcher import BaseFetcher
from ..models import Paper


class OpenReviewFetcher(BaseFetcher):
    source_name = "openreview"

    def fetch(self, query: str, limit: int = 50, **kwargs) -> List[Paper]:
        """`query` is a venue id, e.g. 'ICLR.cc/2024/Conference'."""
        resp = self._get(f"{self.config.openreview_api_endpoint}/notes",
                         params={"content.venueid": query, "limit": limit})
        if resp is None:
            return []
        return [self._note_to_paper(note) for note in resp.json().get("notes", [])]

    # helper to convert OpenReview's note format to our Paper dataclass
    def _note_to_paper(self, note: Dict[str, Any]) -> Paper:
        content = note.get("content", {})

        def val(key):  # v2 wraps fields as {"value": ...}
            v = content.get(key)
            return v.get("value") if isinstance(v, dict) else v

        authors = val("authors") or []
        if not isinstance(authors, list):
            authors = [authors]
        pdf = val("pdf")
        if pdf and pdf.startswith("/"):
            pdf = f"{self.config.openreview_api_endpoint}{pdf}"
        return Paper(
            source=self.source_name,
            source_id=note["id"],
            title=val("title") or "",
            abstract=val("abstract") or "",
            authors=authors,
            categories=val("keywords") or [],
            published=str(note.get("cdate")) if note.get("cdate") else None,
            pdf_url=pdf,
        )
