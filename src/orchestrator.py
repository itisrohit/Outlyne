from typing import Any

import numpy as np
from fastapi import HTTPException

from embedder import VisualEmbedder
from logger import get_logger
from ranker import rank_by_similarity
from search.ddg import DuckDuckGoAdapter
from search.thumbnail_utils import bytes_to_pil, download_all_thumbnails

logger = get_logger(__name__)


class SearchOrchestrator:
    """
    Orchestrates the end-to-end sketch-to-image search pipeline.

    Pipeline:
    1. Convert sketch to embedding (Vision Core)
    2. Generate text query from sketch (future: use CLIP text encoder)
    3. Fetch candidate images from DuckDuckGo (Recall Engine)
    4. Download thumbnails in parallel
    5. Encode thumbnails to embeddings
    6. Rank by visual similarity (Precision Layer)
    """

    def __init__(self, embedder: VisualEmbedder):
        self.embedder = embedder
        self.search_adapter = DuckDuckGoAdapter()

    async def search_by_sketch(
        self, sketch: np.ndarray[Any, Any], text_query: str, max_results: int = 20
    ) -> list[dict[str, Any]]:
        """
        Performs a sketch-to-image search.

        Args:
            sketch: Raw numpy array of the sketch (H x W x 3, RGB).
            text_query: Text query to use for recall (e.g., "modern chair").
            max_results: Maximum number of results to return.

        Returns:
            List of ranked results with similarity scores.
        """
        logger.info("Starting sketch-to-image search for query: '%s'", text_query)

        # Step 1: Encode the sketch (with caching)
        query_embedding = await self.embedder.encode_sketch(sketch)
        logger.info("Sketch encoded to %d-dim embedding", len(query_embedding))

        # Step 2: Recall - Fetch candidates from DuckDuckGo
        search_results = await self.search_adapter.search(text_query, max_results=max_results * 2)

        if not search_results:
            raise HTTPException(status_code=404, detail="No results found from search engine")

        logger.info("Fetched %d candidates from DuckDuckGo", len(search_results))

        # Step 3: Download thumbnails in parallel
        download_pairs = await download_all_thumbnails(search_results)

        # Step 4: Filter successful downloads and encode
        candidate_embeddings = []
        candidate_metadata = []

        for metadata, image_bytes in download_pairs:
            if image_bytes is None:
                continue

            pil_image = bytes_to_pil(image_bytes)
            if pil_image is None:
                continue

            try:
                embedding = self.embedder.encode_image(pil_image)
                candidate_embeddings.append(embedding)
                candidate_metadata.append(metadata)
            except Exception as e:
                logger.debug("Failed to encode image from %s: %s", metadata.get("url"), str(e))

        if not candidate_embeddings:
            raise HTTPException(status_code=500, detail="Failed to encode any candidate images")

        logger.info(
            "Successfully encoded %d/%d candidates",
            len(candidate_embeddings),
            len(search_results),
        )

        # Step 5: Rank by visual similarity
        ranked_results: list[dict[str, Any]] = rank_by_similarity(
            query_embedding, candidate_embeddings, candidate_metadata
        )

        # Return top N
        return ranked_results[:max_results]
