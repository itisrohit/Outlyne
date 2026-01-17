import asyncio
import os
import time
from collections import OrderedDict
from typing import Any, cast

import blake3
import cv2
import numpy as np
import torch
from optimum.intel.openvino import OVModelForFeatureExtraction
from PIL import Image
from transformers import AutoProcessor

from logger import get_logger

logger = get_logger(__name__)


class VisualEmbedder:
    """
    Handles visual embedding generation for both sketches and images using SigLIP2.
    Optimized for CPU inference via OpenVINO.
    """

    def __init__(
        self,
        model_id: str = "google/siglip-base-patch16-224",
        device: str = "CPU",
        model_path: str | None = None,
    ):
        self.device = device

        # Initialize sketch cache (LRU with TTL)
        self._sketch_cache: OrderedDict[str, tuple[np.ndarray[Any, Any], float]] = OrderedDict()
        self._cache_lock = asyncio.Lock()
        self._cache_maxsize = 100
        self._cache_ttl = 600  # 10 minutes

        # Determine if we have a pre-baked model path (e.g., in Docker)
        # Or check if the local export directory already exists to skip export
        effective_path = model_path or os.path.join(".cache", "ov_model")
        has_local_ir = os.path.exists(os.path.join(effective_path, "openvino_model.xml"))

        if has_local_ir:
            logger.info("🚀 Loading pre-baked OpenVINO model from %s", effective_path)
            self.processor = AutoProcessor.from_pretrained(effective_path)  # type: ignore[no-untyped-call]
            self.model = OVModelForFeatureExtraction.from_pretrained(
                effective_path, device=device, export=False
            )
        else:
            logger.info("📦 Exporting visual model to IR (this happens once)...")
            self.processor = AutoProcessor.from_pretrained(model_id, use_fast=True)  # type: ignore[no-untyped-call]
            self.model = OVModelForFeatureExtraction.from_pretrained(
                model_id, export=True, device=device
            )
            # Save it so next time we skip the JIT export
            os.makedirs(effective_path, exist_ok=True)
            self.model.save_pretrained(effective_path)
            self.processor.save_pretrained(effective_path)

    def normalize_sketch(self, sketch_image: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        """
        Prepares raw sketch input for embedding.
        """
        if len(sketch_image.shape) == 3:
            gray = cv2.cvtColor(sketch_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = sketch_image

        # Invert if the background is dark
        if np.mean(gray.astype(np.float32)) < 127:
            gray = cv2.bitwise_not(gray)

        # Denoising
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Contrast stretching
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        if max_val - min_val > 0:
            gray = cv2.convertScaleAbs(
                gray, alpha=255.0 / (max_val - min_val), beta=-min_val * 255.0 / (max_val - min_val)
            )

        return gray

    def encode_text(self, text: list[str]) -> np.ndarray[Any, Any]:
        """
        Generates normalized text embeddings for a list of strings.
        """
        inputs = self.processor(text=text, padding="max_length", max_length=64, return_tensors="pt")

        with torch.no_grad():
            # Create a dummy image for the multi-modal forward pass if needed
            dummy_pixel_values = np.zeros((len(text), 3, 224, 224), dtype=np.float32)
            ov_inputs = {
                "pixel_values": dummy_pixel_values,
                "input_ids": inputs.input_ids.numpy(),
            }
            outputs = self.model.request(ov_inputs)

        # Extract text embeddings
        if "text_embeds" in outputs:
            embeddings = outputs["text_embeds"]
        else:
            # Multi-modal models in OpenVINO often have specific output mappings
            embeddings = next(iter(outputs.values()))

        # L2 Normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return cast(np.ndarray[Any, Any], embeddings / np.maximum(norms, 1e-12))

    def classify_sketch(self, sketch_embedding: np.ndarray[Any, Any]) -> str:
        """
        Heuristic classification of a sketch into broad categories to seed
        web recall when no text query is provided.
        """
        anchors = [
            "chair",
            "shoes",
            "car",
            "watch",
            "lamp",
            "house",
            "mountain",
            "flower",
            "animal",
            "human face",
            "logo",
            "apparel",
            "gadget",
            "bicycle",
            "tree",
            "food",
            "instrument",
            "furniture",
            "bird",
        ]

        # In a real 2026 production app, these would be pre-computed
        anchor_embeddings = self.encode_text(anchors)

        # Dot product for similarity
        scores = np.dot(anchor_embeddings, sketch_embedding)
        best_idx = np.argmax(scores)

        return anchors[best_idx]

    def encode_image(self, image: Image.Image) -> np.ndarray[Any, Any]:
        """
        Generates a normalized visual embedding for a PIL Image.
        """
        inputs = self.processor(
            text=[" "], images=image, padding="max_length", max_length=1, return_tensors="pt"
        )

        with torch.no_grad():
            ov_inputs = {
                "pixel_values": inputs.pixel_values.numpy(),
                "input_ids": inputs.input_ids.numpy(),
            }
            outputs = self.model.request(ov_inputs)

        # Output extraction
        if "image_embeds" in outputs:
            embedding = outputs["image_embeds"][0]
        elif "pooler_output" in outputs:
            embedding = outputs["pooler_output"][0]
        else:
            embedding = next(iter(outputs.values()))[0]

        # L2 Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return cast(np.ndarray[Any, Any], embedding)

    def _compute_sketch_hash(self, sketch_np: np.ndarray[Any, Any]) -> str:
        """
        Computes BLAKE3 hash of sketch bytes for cache key.
        BLAKE3 is faster than SHA256 and provides sufficient uniqueness.
        """
        sketch_bytes = sketch_np.tobytes()
        return blake3.blake3(sketch_bytes).hexdigest()

    async def encode_sketch(self, sketch_np: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        """
        Processes a raw numpy array sketch with caching.
        Repeated sketches return instantly from cache (<1ms).
        """
        sketch_hash = self._compute_sketch_hash(sketch_np)
        current_time = time.time()

        async with self._cache_lock:
            # Check cache
            if sketch_hash in self._sketch_cache:
                embedding, timestamp = self._sketch_cache[sketch_hash]
                # Check TTL
                if current_time - timestamp < self._cache_ttl:
                    # Move to end (LRU)
                    self._sketch_cache.move_to_end(sketch_hash)
                    logger.info("Cache hit for sketch hash: %s", sketch_hash[:8])
                    return embedding
                else:
                    # Expired
                    del self._sketch_cache[sketch_hash]

        # Cache miss - compute embedding
        normalized = self.normalize_sketch(sketch_np)
        pil_image = Image.fromarray(normalized).convert("RGB")
        embedding = self.encode_image(pil_image)

        # Store in cache
        async with self._cache_lock:
            self._sketch_cache[sketch_hash] = (embedding, current_time)
            # Evict oldest if over limit
            if len(self._sketch_cache) > self._cache_maxsize:
                self._sketch_cache.popitem(last=False)

        return embedding


if __name__ == "__main__":
    import asyncio
    import time

    from logger import setup_logging

    setup_logging()

    embedder = VisualEmbedder()
    dummy_sketch = np.ones((224, 224, 3), dtype=np.uint8) * 255
    cv2.line(dummy_sketch, (50, 50), (150, 150), (0, 0, 0), 2)

    async def test_encoding() -> None:
        start = time.time()
        vec = await embedder.encode_sketch(dummy_sketch)
        logger.info("Embedding shape: %s", vec.shape)
        logger.info("Inference time: %.2fms", (time.time() - start) * 1000)

    asyncio.run(test_encoding())
