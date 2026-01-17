import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from logger import get_logger, setup_logging
from search.ddg import DuckDuckGoAdapter
from search.thumbnail_utils import download_all_thumbnails

setup_logging()
logger = get_logger(__name__)


async def test_search() -> None:
    logger.info("Starting Recall Engine Test...")

    adapter = DuckDuckGoAdapter()
    query = "modern minimalist chair design"

    # 1. Search
    results = await adapter.search(query, max_results=10)

    if not results:
        logger.error("No results found. Search might be blocked or failed.")
        return

    # 2. Download Thumbnails
    logger.info("Downloading thumbnails in parallel...")
    result_pairs = await download_all_thumbnails(results)

    success_count = sum(1 for _, data in result_pairs if data is not None)

    logger.info("--- Test Results ---")
    logger.info("Total Search Hits: %d", len(results))
    logger.info("Successfully Downloaded: %d", success_count)

    for i, (res, data) in enumerate(result_pairs[:3]):
        status = "✅ OK" if data else "❌ Failed"
        logger.info("Result %d: %s | Status: %s", i + 1, res["title"][:50], status)


if __name__ == "__main__":
    asyncio.run(test_search())
