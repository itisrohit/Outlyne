import sys
import time
from pathlib import Path

import cv2
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from embedder import VisualEmbedder
from logger import get_logger, setup_logging

logger = get_logger(__name__)


def main() -> None:
    setup_logging()
    logger.info("--- 🚀 Outlyne Embedder Benchmark ---")

    # Initialize
    start_init = time.time()
    # Cache is handled internally by VisualEmbedder defaults
    embedder = VisualEmbedder()
    logger.info("Initialization took: %.2fs", time.time() - start_init)

    # Prepare dummy sketch (a simple circle)
    canvas = np.ones((400, 400, 3), dtype=np.uint8) * 255
    cv2.circle(canvas, (200, 200), 100, (0, 0, 0), 5)

    # Warmup
    logger.info("Warming up...")
    embedder.encode_sketch(canvas)

    # Benchmarking
    iterations = 5
    latencies = []

    logger.info("Running %d iterations...", iterations)
    for i in range(iterations):
        t0 = time.time()
        vec = embedder.encode_sketch(canvas)
        t1 = time.time()
        latencies.append((t1 - t0) * 1000)
        logger.info("  Iteration %d: %.2fms", i + 1, latencies[-1])

    avg_latency = np.mean(latencies)
    logger.info("--- Results ---")
    logger.info("Average Latency: %.2fms", avg_latency)
    logger.info("Embedding Dimensions: %d", len(vec))

    if avg_latency < 200:
        logger.info("✅ Performance within acceptable bounds.")
    else:
        logger.warning("⚠️ Latency higher than ideal.")


if __name__ == "__main__":
    main()
