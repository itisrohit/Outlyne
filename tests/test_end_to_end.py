import asyncio
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from embedder import VisualEmbedder
from logger import get_logger, setup_logging
from orchestrator import SearchOrchestrator

setup_logging()
logger = get_logger(__name__)


def create_test_sketch() -> np.ndarray[Any, Any]:
    """Creates a simple test sketch of a chair."""
    img = Image.new("RGB", (224, 224), color="white")
    draw = ImageDraw.Draw(img)

    # Draw a simple chair shape
    # Seat
    draw.rectangle([50, 100, 170, 120], fill="black")
    # Back
    draw.rectangle([50, 50, 70, 100], fill="black")
    # Legs
    draw.rectangle([55, 120, 65, 170], fill="black")
    draw.rectangle([155, 120, 165, 170], fill="black")

    return np.array(img)


async def test_end_to_end() -> None:
    logger.info("=== Starting End-to-End Pipeline Test ===")

    # Step 1: Initialize components
    logger.info("Initializing Vision Core...")
    embedder = VisualEmbedder()
    orchestrator = SearchOrchestrator(embedder)

    # Step 2: Create test sketch
    logger.info("Creating test sketch...")
    sketch = create_test_sketch()

    # Step 3: Run search
    query = "modern minimalist chair"
    max_results = 10

    logger.info("Running search for: '%s'", query)
    results = await orchestrator.search_by_sketch(
        sketch=sketch, text_query=query, max_results=max_results
    )

    # Step 4: Display results
    logger.info("=== Search Results ===")
    logger.info("Query: %s", query)
    logger.info("Total Results: %d", len(results))
    logger.info("")

    for i, result in enumerate(results[:5], 1):
        logger.info("Result %d:", i)
        logger.info("  Title: %s", result.get("title", "N/A")[:60])
        logger.info("  Similarity: %.4f", result.get("similarity_score", 0.0))
        logger.info("  URL: %s", result.get("url", "N/A")[:80])
        logger.info("")

    # Verify results
    assert len(results) > 0, "No results returned"
    assert all("similarity_score" in r for r in results), "Missing similarity scores"
    assert results[0]["similarity_score"] >= results[-1]["similarity_score"], "Results not sorted"

    logger.info("✅ End-to-end test passed!")


if __name__ == "__main__":
    asyncio.run(test_end_to_end())
