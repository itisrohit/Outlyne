import os
from typing import Any, cast

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
        
        # Determine if we have a pre-baked model path (e.g., in Docker)
        # Or check if the local export directory already exists to skip export
        effective_path = model_path or os.path.join(".cache", "ov_model")
        has_local_ir = os.path.exists(os.path.join(effective_path, "openvino_model.xml"))

        if has_local_ir:
            logger.info("🚀 Loading pre-baked OpenVINO model from %s", effective_path)
            self.processor = AutoProcessor.from_pretrained(effective_path) # type: ignore[no-untyped-call]
            self.model = OVModelForFeatureExtraction.from_pretrained(
                effective_path, device=device, export=False
            )
        else:
            logger.info("📦 Exporting visual model to IR (this happens once)...")
            self.processor = AutoProcessor.from_pretrained(model_id, use_fast=True) # type: ignore[no-untyped-call]
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

    def encode_image(self, image: Image.Image) -> np.ndarray[Any, Any]:
        """
        Generates a normalized visual embedding for a PIL Image.
        """
        inputs = self.processor(
            text=[" "], 
            images=image, 
            padding="max_length", 
            max_length=1, 
            return_tensors="pt"
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

    def encode_sketch(self, sketch_np: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        """
        Processes a raw numpy array sketch.
        """
        normalized = self.normalize_sketch(sketch_np)
        pil_image = Image.fromarray(normalized).convert("RGB")
        return self.encode_image(pil_image)


if __name__ == "__main__":
    from logger import setup_logging
    setup_logging()
    
    embedder = VisualEmbedder()
    dummy_sketch = np.ones((224, 224, 3), dtype=np.uint8) * 255
    cv2.line(dummy_sketch, (50, 50), (150, 150), (0, 0, 0), 2)

    import time
    start = time.time()
    vec = embedder.encode_sketch(dummy_sketch)
    
    logger.info("Embedding shape: %s", vec.shape)
    logger.info("Inference time: %.2fms", (time.time() - start) * 1000)
