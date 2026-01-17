# Outlyne
> AI-powered sketch-to-image meta search engine with sub-second perceived latency.

Outlyne uses **SigLIP2** and **OpenVINO** to convert hand-drawn sketches into visual embeddings in real-time (~90ms), then performs live meta-searches across the internet to find visually similar matches.

---

## 🛠 Prerequisites
Ensure you have the following installed:
- **Python 3.12+**
- **Bun** (Fast JavaScript/Task Runner)
- **uv** (Extremely fast Python package manager)
- **Docker** (Recommended for production-like performance)

---

## 🚀 Getting Started (First Time Setup)

### 1. Clone & Install
```bash
# Install dependencies & setup local cache
bun run sync
```

### 2. Verify Vision Core (Benchmarks)
Run the dedicated benchmark to verify inference speed and model optimization:
```bash
uv run python tests/bench_embedder.py
```

### 3. Start Development
Choose between running locally for rapid logic changes or via Docker for high-performance "baked" model serving.

**Local Development:**
```bash
# Start the FastAPI Backend
bun run dev:api

# Start the React Frontend (Phase 4)
bun run dev:web
```

**Dockerized (Recommended for Speed):**
```bash
# Build the image & bake the OpenVINO model (Initial build: 3-5 mins)
bun run docker:build

# Launch the container (Cold start: ~2s)
bun run docker:up
```

---

## 🔧 Developer Commands

| Command | Description |
| :--- | :--- |
| `bun run sync` | Sync Python venv & setup cache dirs |
| `bun run lint` | Run Ruff & Mypy strict checks |
| `bun run docker:build` | Bake model artifacts into Docker image |
| `bun run docker:up` | Spin up the orchestrated stack |
| `bun run clean` | Remove all caches, venv, and artifacts |

---

## 📈 Current Performance
- **Visual Encoding:** **~92.7ms** 🔥 (SigLIP2 on CPU via OpenVINO)
- **Cold Boot (Docker):** **~2s** (Vs. 45s locally without pre-baked IR)
- **Memory Footprint:** ~813MB (Model weights in buffer)
- **Lints:** 100% clean (Strict Mypy + Ruff)
