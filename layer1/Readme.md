# The implementation of the paper-fetching layer is organized into focused modules:

- `config.py`            : configuration settings for fetchers and coordinator

- `models.py`            : the `Paper` data model
- `coordinator.py`       : the `Coordinator` class that manages fetchers and merges results
- `base_fetcher.py`      : `BaseFetcher` (HTTP, storage, GROBID, ingest pipeline)

- `fetchers/arxiv.py`    : `ArxivFetcher`
- `fetchers/semantic_scholar.py` : `SemanticScholarFetcher`
- `fetchers/openreview.py`: `OpenReviewFetcher`

## how we will use it:

call `coordinator.fetch_papers(query)` to get a list of `Paper` objects matching the query, with metadata from all sources merged together. The coordinator will handle deduplication and merging of records from different sources.