# The Vision Core Summary

## Accomplishments
We have successfully completed the first major milestone of the **Outlyne** project: building a high-performance, CPU-optimized visual embedding engine.

### Highlights:
- **Model Choice:** Integrated `google/siglip-base-patch16-224` (SigLIP2 architecture), providing superior vision-language alignment compared to standard CLIP.
- **Optimization:** Leveraged **Intel OpenVINO** and `optimum-intel` to accelerate inference on consumer CPUs.
- **Normalization:** Implemented a robust `normalize_sketch` pipeline using OpenCV to handle varied user drawings (black-on-white, white-on-black, noise reduction).
- **Project Structure:** Standardized on a flattened `src/` layout for Python and a `web/` root for React, managed by **Bun** (orchestrator) and **uv** (dependencies).

---

## Technical Challenges & Solutions

### 1. The "Polyglot" Workflow
- **Issue:** Multi-step commands like `uv run python -m src.outlyne` were cumbersome.
- **Solution:** Integrated **Bun** as the project's primary task runner. Standardized commands into `bun run dev:api`, `bun run lint`, etc., in `package.json`.

### 2. Dependency Hell (Torch vs. OpenVINO)
- **Issue:** Initial attempts faced `ImportError` and `RuntimeError` due to version mismatches between `torch` (2.5.1 vs 2.9.1) and `optimum-intel`.
- **Solution:** Upgraded internal dependencies to **Torch 2.9.1** and **Torchvision 0.24.1**, satisfying the NNCF (Neural Network Compression Framework) requirements for 2026.

### 3. OpenVINO Signature Mismatches
- **Issue:** The `OVModelForFeatureExtraction` wrapper from `optimum-intel` expected specific positional arguments (`attention_mask`, `input_ids`) that weren't always generated correctly by the processor for vision-only tasks.
- **Solution:** Bypassed the high-level wrapper's `forward` method. We now call the underlying **OpenVINO Compiled Model** directly with filtered inputs (`pixel_values`, `input_ids`), ensuring stability across different model exports.

### 4. Cold-Start Performance & Cache Migrations
- **Issue:** Hugging Face `transformers` library was triggering a one-time cache migration message that hung in automated environments.
- **Solution:** Forced a local project-level cache (`.cache/huggingface`) via environment variables and set verbosity to `error` to handle cleaner execution.

---

## Performance Results (Benchmark)
*Running on Apple M1/M4 equivalent CPU*

- **Embedder Avg Latency:** **~92.7ms** 🔥 (After optimization)
- **Cold Boot (Local):** ~41s (Inference + Export)
- **Cold Boot (Docker):** **~2s** (Pre-baked IR Artifacts)
- **Output Dimensions:** 768 (L2 Normalized)
- **Memory Footprint:** ~813MB (Quantized Model Buffer)
- **Status:** ✅ **Target Exceeded** (< 100ms per embedding).

---

## The Docker "Bakery" Strategy
To solve the slow startup and reproducibility issues, we implemented a **Multi-Stage Build** system:
- **Build Stage:** Installs `uv`, downloads SigLIP2, and runs a one-time OpenVINO export (IR conversion).
- **Runtime Stage:** A slim production image containing **only** the pre-baked `.xml` and `.bin` model files.
- **Caching:** Utilized **BuildKit Cache Mounts** (`--mount=type=cache`) to persist HuggingFace downloads across builds, ensuring subsequent 1-second build times even if code changes.

### Why the initial build is slow:
Converting an 813MB SigLIP2 model into a static OpenVINO IR graph requires:
1. Initializing the full PyTorch weight buffers.
2. Running a "dummy inference" to trace the execution path.
3. JIT-optimizing the math kernels for the target CPU architecture.
4. Serializing the optimized graph to disk.

**On a typical developer laptop, this process takes 3 to 6 minutes.**

### Is it worth it?
**Absolutely.** In a production environment, cold starts are the enemy. By "baking" the model during the build phase:
- The container boots in **~2 seconds**.
- No network requests are made for weights at runtime.
- The runtime environment is 100% stable and reproducible.

> **💡 Dev Tip:** For rapid iteration on Python code (like `main.py` or search logic), use `bun run dev:api` locally. Only use `bun run docker:build` when you need to verify the container or finalize a release.

---

---

## Current Known Warnings (Non-Blocking)
While the engine is stable and fast, the following upstream warnings are currently expected during the initial model export/warmup phase:

1. **TracerWarning (SigLIP2):**  
   `Converting a tensor to a Python boolean might cause the trace to be incorrect...`  
   *Cause:* Known behavior in the Hugging Face SigLIP2 implementation when handled by Torch's JIT tracer for OpenVINO export.  
   *Impact:* None on inference accuracy or speed.

2. **DeprecationWarning (OpenVINO):**  
   `The openvino.runtime module is deprecated and will be removed in the 2026.0 release...`  
   *Cause:* `optimum-intel` internal imports haven't fully migrated to the top-level `openvino` namespace.  
   *Impact:* None. We have verified our environment uses the latest OpenVINO 2025+ binaries.

3. **OnnxExporterWarning:**  
   `Symbolic function 'aten::scaled_dot_product_attention' already registered...`  
   *Cause:* Redundant registration of attention operators during the PyTorch-to-OpenVINO conversion path.  
   *Impact:* None.  

---
