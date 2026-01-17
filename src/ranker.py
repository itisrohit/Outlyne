from typing import Any

import numpy as np

from logger import get_logger

logger = get_logger(__name__)


def rank_by_similarity(
    query_embedding: np.ndarray[Any, Any],
    candidate_embeddings: list[np.ndarray[Any, Any]],
    candidate_metadata: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Ranks candidates by visual similarity to the query embedding.

    Since embeddings are L2-normalized, dot product == cosine similarity.
    This is significantly faster than computing cosine similarity manually.

    Args:
        query_embedding: The normalized query embedding (768-dim for SigLIP2).
        candidate_embeddings: List of normalized candidate embeddings.
        candidate_metadata: List of metadata dicts (url, title, etc.) for each candidate.

    Returns:
        List of metadata dicts, sorted by descending similarity score.
    """
    if len(candidate_embeddings) != len(candidate_metadata):
        raise ValueError("Mismatch between embeddings and metadata counts")

    if len(candidate_embeddings) == 0:
        return []

    # Stack all candidate embeddings into a matrix (N x 768)
    candidates_matrix = np.vstack(candidate_embeddings)

    # Compute dot products (equivalent to cosine similarity for normalized vectors)
    # Shape: (N,)
    similarities = candidates_matrix @ query_embedding

    # Sort indices by descending similarity
    sorted_indices = np.argsort(similarities)[::-1]

    # Build ranked results
    ranked_results = []
    for idx in sorted_indices:
        result = candidate_metadata[idx].copy()
        result["similarity_score"] = float(similarities[idx])
        ranked_results.append(result)

    logger.info(
        "Ranked %d candidates. Top score: %.4f, Bottom score: %.4f",
        len(ranked_results),
        ranked_results[0]["similarity_score"] if ranked_results else 0.0,
        ranked_results[-1]["similarity_score"] if ranked_results else 0.0,
    )

    return ranked_results
