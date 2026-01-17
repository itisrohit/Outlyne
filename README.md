# Outlyne
> AI-powered sketch-to-image meta search engine with zero-shot visual discovery.

Outlyne uses **SigLIP2** and **OpenVINO** to convert hand-drawn sketches into visual embeddings in real-time (~90ms). It features a **Zero-Shot Semantic Interrogator** that interprets your visual intent to perform live searches across the internet—finding matching products and imagery even with zero text input.

---

## 🛠 Prerequisites
Ensure you have the following installed:
- **Python 3.12+**
- **Bun** (Fast JavaScript/Task Runner)
- **uv** (Extremely fast Python package manager)
- **Docker** (Recommended for optimized performance)

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
Outlyne now features a unified development command that orchestrates both the API and the Web frontend:

**Orchestrated Local Development:**
```bash
# Start both Backend + Frontend in sync
bun run dev
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
| `bun run dev` | **Unified Dev**: Starts API and Web frontend concurrently |
| `bun run sync` | Sync Python venv & setup cache dirs |
| `bun run lint` | Run Ruff, Mypy, and Biome strict checks across the stack |
| `bun run test` | Run the Zero-Shot sketch search verification suite |
| `bun run docker:build` | Bake model artifacts into Docker image |
| `bun run docker:up` | Spin up the orchestrated stack |
| `bun run clean` | Remove all caches, venv, and artifacts |

---

## 📈 Current Performance
- **Visual Encoding:** **~92.7ms** 🔥 (SigLIP2 on CPU via OpenVINO)
- **Semantic Interrogation:** **~12ms** (Zero-shot intent classification)
- **Cold Boot (Docker):** **~2s** (Vs. 45s locally without pre-baked IR)
- **Memory Footprint:** ~813MB (Model weights in buffer)
- **Lints:** 100% clean (Strict Mypy + Ruff + Biome)
