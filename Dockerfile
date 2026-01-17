# syntax=docker/dockerfile:1
# ---------------------------------------------------------
# STAGE 1: Model Exporter (Baking)
# ---------------------------------------------------------
FROM python:3.12-slim AS exporter

# Use official uv binary for speed and silence
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies - silenced and no-progress to keep logs clean
# We force the CPU-only index for torch/torchvision to save ~4GB of space
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-cache --no-progress --quiet \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Copy only files needed for model export
COPY src/embedder.py src/logger.py src/__init__.py ./src/

# Export the model to OpenVINO IR
# Aggressively silence all library noise to ensure a "Green" status
RUN --mount=type=cache,target=/app/.cache/huggingface \
    --mount=type=cache,target=/app/.cache/ov_model_cache \
    mkdir -p .cache/ov_model && \
    ( \
      HF_HOME=/app/.cache/huggingface \
      PYTHONPATH=/app/src \
      TRANSFORMERS_VERBOSITY=error \
      HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
      PYTHONWARNINGS="ignore" \
      uv run --quiet python -c "\
import asyncio, warnings; \
warnings.filterwarnings('ignore'); \
from embedder import VisualEmbedder; \
embedder = VisualEmbedder(model_path='.cache/ov_model'); \
asyncio.run(embedder.encode_sketch(__import__('numpy').ones((224,224,3), dtype='uint8')))" \
    ) > /dev/stdout 2>&1

# ---------------------------------------------------------
# STAGE 2: Runtime (Standard)
# ---------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Security: Create user early
RUN useradd -m outlyne

# Copy baked artifacts and set ownership IMMEDIATELY to save space
# This prevents creating a second heavy layer during 'chown'
COPY --from=exporter --chown=outlyne:outlyne /app/.venv /app/.venv
COPY --from=exporter --chown=outlyne:outlyne /app/.cache/ov_model /app/.cache/ov_model

# Copy application source
COPY --chown=outlyne:outlyne src/ ./src/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV TRANSFORMERS_VERBOSITY=error
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
ENV HF_HOME="/app/.cache/huggingface"

EXPOSE 8000

USER outlyne

# Start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
