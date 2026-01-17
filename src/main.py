import base64
import io
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel

from embedder import VisualEmbedder
from logger import get_logger, setup_logging
from orchestrator import SearchOrchestrator

setup_logging()
logger = get_logger(__name__)


class SearchRequest(BaseModel):
    sketch_base64: str
    query: str
    max_results: int = 20


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Load the ML model
    logger.info("Starting up: Loading Vision Core...")
    app.state.embedder = VisualEmbedder()
    app.state.orchestrator = SearchOrchestrator(app.state.embedder)
    logger.info("Vision Core and Orchestrator loaded successfully.")
    yield
    # Clean up
    logger.info("Shutting down...")


app = FastAPI(title="Outlyne API", lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "message": "Outlyne API is running",
        "vision_core": "loaded" if hasattr(app.state, "embedder") else "not_loaded",
        "orchestrator": "loaded" if hasattr(app.state, "orchestrator") else "not_loaded",
    }


@app.post("/search")
async def search(request: SearchRequest) -> dict[str, Any]:
    """
    Sketch-to-image search endpoint.

    Accepts a base64-encoded sketch and a text query,
    returns ranked image results based on visual similarity.
    """
    try:
        # Decode base64 sketch
        sketch_bytes = base64.b64decode(request.sketch_base64)
        sketch_image = Image.open(io.BytesIO(sketch_bytes)).convert("RGB")
        sketch_np = np.array(sketch_image)

        # Run the search pipeline
        results = await app.state.orchestrator.search_by_sketch(
            sketch=sketch_np, text_query=request.query, max_results=request.max_results
        )

        return {"query": request.query, "results": results, "count": len(results)}

    except Exception as e:
        logger.error("Search failed: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}") from None


def main() -> None:
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
