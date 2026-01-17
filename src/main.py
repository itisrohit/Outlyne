from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from embedder import VisualEmbedder
from logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Load the ML model
    logger.info("Starting up: Loading Vision Core...")
    # This will use the pre-baked model if running in Docker
    app.state.embedder = VisualEmbedder()
    logger.info("Vision Core loaded successfully.")
    yield
    # Clean up
    logger.info("Shutting down...")


app = FastAPI(title="Outlyne API", lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "message": "Outlyne API is running",
        "vision_core": "loaded" if hasattr(app.state, "embedder") else "not_loaded",
    }


def main() -> None:
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
