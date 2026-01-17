import os

# Silence Transformers cache migration and set local cache
os.environ["HF_HOME"] = os.path.join(os.getcwd(), ".cache", "huggingface")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import sys
import numpy as np
import cv2
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from embedder import VisualEmbedder

def main():
    print("--- 🚀 Outlyne Embedder Benchmark ---")
    
    # Initialize
    start_init = time.time()
    # Using a standard siglip model that is well supported
    embedder = VisualEmbedder(model_id="google/siglip-base-patch16-224")
    print(f"Initialization took: {time.time() - start_init:.2f}s")

    # Prepare dummy sketch (a simple circle)
    canvas = np.ones((400, 400, 3), dtype=np.uint8) * 255
    cv2.circle(canvas, (200, 200), 100, (0, 0, 0), 5)

    # Warmup
    print("Warming up...")
    embedder.encode_sketch(canvas)

    # Benchmarking
    iterations = 5
    latencies = []

    print(f"Running {iterations} iterations...")
    for i in range(iterations):
        t0 = time.time()
        vec = embedder.encode_sketch(canvas)
        t1 = time.time()
        latencies.append((t1 - t0) * 1000)
        print(f"  Iteration {i+1}: {latencies[-1]:.2f}ms")

    avg_latency = np.mean(latencies)
    print("--- Results ---")
    print(f"Average Latency: {avg_latency:.2f}ms")
    print(f"Embedding Dimensions: {len(vec)}")
    
    # Target check (from plan.md: < 800ms cold, including search)
    # The embedder itself should ideally be < 100ms on modern CPU.
    if avg_latency < 200:
        print("✅ Performance within acceptable bounds for local re-ranking.")
    else:
        print("⚠️ Latency higher than ideal. Consider further quantization (INT8).")

if __name__ == "__main__":
    main()
