<div align="center">
  <img src="./assets/banner.png" alt="Outlyne Banner" width="90%" />

  <br />

  **AI-powered sketch-to-image meta search engine with zero-shot visual discovery.**

  <br />

  <img src="./assets/demo.gif" alt="Outlyne Demo" width="95%" />
  
  <br />
  
  <sub>Sketch → visual intent → live internet results (no text input).</sub>

  <br />

  <p align="center">
    <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
    <a href="https://docs.openvino.ai"><img src="https://img.shields.io/badge/OpenVINO-2025-purple?style=for-the-badge&logo=intel&logoColor=white" alt="OpenVINO"></a>
    <a href="https://react.dev"><img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"></a>
    <a href="https://docker.com"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
    <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
  </p>
</div>

<br />

Outlyne uses **SigLIP2** and **OpenVINO** to convert hand-drawn sketches into visual embeddings in real-time (~90ms). It features a **zero-shot visual intent layer** that interprets sketches to perform live image search across public engines, requiring no text input.

## Why Outlyne?

Traditional image search requires text. Outlyne flips the interaction: you sketch first, the system infers intent visually, then searches live.

**No indexing. No training. No prompts.**

---

## Prerequisites

Ensure you have the following installed before starting:
- **[Python 3.12+](https://www.python.org/)**
- **[Bun](https://bun.sh/)** (JavaScript/TypeScript Task Runner)
- **[uv](https://github.com/astral-sh/uv)** (Fast Python package manager)
- **[Docker](https://www.docker.com/)** (Recommended for production-like environment)

---

## Getting Started

### 1. Clone & Install
```bash
git clone https://github.com/itisrohit/Outlyne.git
cd Outlyne

# Install dependencies & setup local cache
bun run sync
```

### 2. Verify Vision Core
Run the dedicated benchmark to verify proper model optimization and inference speed:
```bash
uv run python tests/bench_embedder.py
```

### 3. Start Development
Outlyne features a unified development command that orchestrates both the Python API and the React frontend:

**Local Development:**
```bash
# Start both Backend + Frontend in sync
bun run dev
```

**Docker (Recommended for Backend):**
```bash
# 1. Build & Launch the API Container
bun run docker:build
bun run docker:up

# 2. Start the Frontend (in a new terminal)
cd web && bun run dev
```

---

## Developer Commands

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

## Performance Benchmarks

- **Visual Encoding:** **~92.7ms** 🔥 (SigLIP2 on CPU via OpenVINO)
- **Semantic Interrogation:** **~12ms** (Zero-shot intent classification)
- **Cold Boot (Docker):** **~2s** (Vs. 45s locally without pre-baked IR)
- **Lints:** 100% clean (Strict Mypy + Ruff + Biome)

---

## Documentation
- **[Contributing](./CONTRIBUTING.md)** - Guidelines for contributing to Outlyne.
- **[Architecture](./docs/architecture.md)** - Deep dive into system design and components.
- **[Vision Core](./docs/vision_core_implementation.md)** - Implementation details of the visual engine.
