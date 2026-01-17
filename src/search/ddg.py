from typing import Any

from ddgs import DDGS

from logger import get_logger

from .base import BaseSearchAdapter

logger = get_logger(__name__)


class DuckDuckGoAdapter(BaseSearchAdapter):
    """
    Adapter for DuckDuckGo Image Search.
    Utilizes the 'ddgs' library for free image search.
    """

    async def search(self, query: str, max_results: int = 50) -> list[dict[str, Any]]:
        logger.info("Searching DuckDuckGo for: '%s'", query)

        results: list[dict[str, Any]] = []
        try:
            # DDGS is synchronous, but we can run it in the event loop
            # since it's I/O bound and relatively fast
            ddgs = DDGS()
            ddgs_results = ddgs.images(
                query=query,
                region="wt-wt",
                safesearch="moderate",
                max_results=max_results,
                backend="auto",
            )

            for r in ddgs_results:
                results.append(
                    {
                        "url": r.get("image"),
                        "thumbnail": r.get("thumbnail"),
                        "title": r.get("title"),
                        "source": "duckduckgo",
                    }
                )

            logger.info("Found %d results from DuckDuckGo", len(results))

        except Exception as e:
            logger.error("DuckDuckGo search failed for '%s': %s", query, str(e))

        return results
