# Outlyne
> AI-powered sketch-to-image meta search engine with sub-second perceived latency.

Outlyne uses **SigLIP2** and **OpenVINO** to convert hand-drawn sketches into visual embeddings in real-time (~100ms), then performs live meta-searches across the internet to find visually similar matches.

---

## 🛠 Prerequisites
Ensure you have the following installed:
- **Python 3.12+**
- **Bun** (Fast JavaScript/Task Runner)
- **uv** (Extremely fast Python package manager)

---

## 🚀 Getting Started (First Time Setup)

### 1. Clone & Install
```bash
# Install dependencies & setup local cache
bun run sync
```

### 2. Verify Vision Core (Benchmarks)
Run this to download the model, export it to OpenVINO, and verify inference speed:
```bash
bun run dev:api  # This will trigger the initial model download & export
# OR run the dedicated benchmark
uv run python tests/bench_embedder.py
```

### 3. Start Development
```bash
# Start the FastAPI Backend
bun run dev:api

# Start the React Frontend (Phase 4)
bun run dev:web
```

---

## 🔧 Developer Commands

| Command | Description |
| :--- | :--- |
| `bun run sync` | Sync Python virtual environment |
| `bun run lint` | Run Ruff & Mypy strict checks |
| `bun run format` | Auto-format Python code |
| `bun run test` | Run pytest suite |
| `bun run clean` | Remove all caches and venv |

---

## 📈 Current Performance
- **Visual Encoding:** ~93ms (SigLIP2 on CPU via OpenVINO)
- **Memory Footprint:** ~800MB
- **Lints:** 100% clean (Strict Mypy + Ruff)
