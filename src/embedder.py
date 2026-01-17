# Silence Transformers cache migration and set local cache
import os
import warnings
os.environ["HF_HOME"] = os.path.join(os.getcwd(), ".cache", "huggingface")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Suppress specific TracerWarnings often seen during OpenVINO export
warnings.filterwarnings("ignore", category=UserWarning, module="transformers.models.siglip.modeling_siglip")

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoProcessor
from optimum.intel.openvino import OVModelForFeatureExtraction

class VisualEmbedder:
    """
    Handles visual embedding generation for both sketches and images using SigLIP2.
    Optimized for CPU inference via OpenVINO.
    """
    
    def __init__(self, model_id: str = "google/siglip-base-patch16-224", device: str = "CPU"):
        self.device = device
        print(f"Initializing VisualEmbedder with {model_id} on {device}...")
        
        # Load processor with use_fast=True to avoid warnings
        self.processor = AutoProcessor.from_pretrained(model_id, use_fast=True)
        
        # Load OpenVINO optimized model
        self.model = OVModelForFeatureExtraction.from_pretrained(
            model_id, 
            export=True, 
            device=device
        )
        
    def normalize_sketch(self, sketch_image: np.ndarray) -> np.ndarray:
        """
        Prepares raw sketch input for embedding:
        - Grayscale conversion
        - Edge enhancement / Denoising
        - Contrast stretching
        """
        if len(sketch_image.shape) == 3:
            gray = cv2.cvtColor(sketch_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = sketch_image
            
        # Invert if the background is dark (sketches are usually black on white)
        if np.mean(gray) < 127:
            gray = cv2.bitwise_not(gray)
            
        # Denoising
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Contrast stretching
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        if max_val - min_val > 0:
            gray = cv2.convertScaleAbs(gray, alpha=255.0/(max_val-min_val), beta=-min_val * 255.0/(max_val-min_val))
            
        return gray

    def encode_image(self, image: Image.Image) -> np.ndarray:
        """
        Generates a normalized visual embedding for a PIL Image.
        """
        # We must provide some text tokens as SigLIP is a vision-language model 
        # but we only pass the tags that the OpenVINO model actually expects.
        # Most SigLIP exports for OpenVINO expect 'input_ids' and 'pixel_values'.
        # Note: when using fast processor, it behaves slightly differently.
        inputs = self.processor(text=[" "], images=image, padding="max_length", max_length=1, return_tensors="pt")
        
        # OpenVINO inference - specifically targeting the compiled model to bypass 
        # any wrapper signature mismatches.
        with torch.no_grad():
            # Use the underlying CompiledModel for direct control
            # We filter inputs to only what the model actually accepts
            ov_inputs = {
                "pixel_values": inputs.pixel_values.numpy(),
                "input_ids": inputs.input_ids.numpy()
            }
            
            # Call the model directly
            outputs = self.model.request(ov_inputs)
            
        # SigLIP multimodal model output processing
        # OpenVINO results are a dictionary of {tensor_name: ndarray}
        # We look for the image embedding output.
        if "image_embeds" in outputs:
            embedding = outputs["image_embeds"][0]
        elif "pooler_output" in outputs:
            embedding = outputs["pooler_output"][0]
        else:
            # Fallback: take the largest or first output
            # Usually the embedding is the 1D/2D tensor
            embedding = next(iter(outputs.values()))[0]
            
        # L2 Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding

    def encode_sketch(self, sketch_np: np.ndarray) -> np.ndarray:
        """
        Processes a raw numpy array sketch and returns its embedding.
        """
        normalized = self.normalize_sketch(sketch_np)
        pil_image = Image.fromarray(normalized).convert("RGB")
        return self.encode_image(pil_image)

if __name__ == "__main__":
    # Quick bench test
    embedder = VisualEmbedder()
    dummy_sketch = np.ones((224, 224, 3), dtype=np.uint8) * 255
    cv2.line(dummy_sketch, (50, 50), (150, 150), (0, 0, 0), 2)
    
    import time
    start = time.time()
    vec = embedder.encode_sketch(dummy_sketch)
    end = time.time()
    
    print(f"Embedding shape: {vec.shape}")
    print(f"Inference time: {(end - start) * 1000:.2f}ms")
    print(f"Success.")
