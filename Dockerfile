# syntax=docker/dockerfile:1
# ---------------------------------------------------------
# STAGE 1: Model Exporter (Baking)
# ---------------------------------------------------------
FROM python:3.12-slim AS exporter

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using a cache mount for uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Copy only files needed for model export
COPY src/embedder.py src/logger.py src/__init__.py ./src/

# Export the model to OpenVINO IR
# We use a cache mount for BOTH HuggingFace and the local OV cache.
# This makes subsequent builds near-instant.
RUN --mount=type=cache,target=/app/.cache/huggingface \
    --mount=type=cache,target=/app/.cache/ov_model_cache \
    mkdir -p .cache/ov_model && \
    HF_HOME=/app/.cache/huggingface \
    PYTHONPATH=/app/src \
    TRANSFORMERS_VERBOSITY=error \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
    uv run python -c "\
import asyncio; \
from embedder import VisualEmbedder; \
embedder = VisualEmbedder(model_path='.cache/ov_model'); \
asyncio.run(embedder.encode_sketch(__import__('numpy').ones((224,224,3), dtype='uint8')))"

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

# Copy baked artifacts
COPY --from=exporter /app/.venv /app/.venv
COPY --from=exporter /app/.cache/ov_model /app/.cache/ov_model

# Copy application source
COPY src/ ./src/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV TRANSFORMERS_VERBOSITY=error
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
ENV HF_HOME="/app/.cache/huggingface"

EXPOSE 8000

# Security
RUN useradd -m outlyne && chown -R outlyne:outlyne /app
USER outlyne

# Start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
