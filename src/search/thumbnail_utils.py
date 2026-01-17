import asyncio
import io
from typing import Any

import httpx
from PIL import Image

from logger import get_logger

logger = get_logger(__name__)


async def download_thumbnail(
    client: httpx.AsyncClient, url: str, timeout: float = 5.0
) -> bytes | None:
    """
    Downloads raw image bytes for a single thumbnail.
    """
    try:
        response = await client.get(url, timeout=timeout, follow_redirects=True)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logger.debug("Failed to download thumbnail from %s: %s", url, str(e))
    return None


async def download_all_thumbnails(
    results: list[dict[str, Any]], max_concurrent: int = 15
) -> list[tuple[dict[str, Any], bytes | None]]:
    """
    Downloads thumbnails for a list of search results in parallel.
    Limits concurrency to avoid overloading the network/local stack.
    """
    timeout = httpx.Timeout(5.0, connect=2.0)
    async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def sem_download(item: dict[str, Any]) -> tuple[dict[str, Any], bytes | None]:
            url = item.get("thumbnail") or item.get("url")
            if not url:
                return item, None

            async with semaphore:
                data = await download_thumbnail(client, url)
                return item, data

        tasks = [sem_download(res) for res in results]
        return await asyncio.gather(*tasks)


def bytes_to_pil(image_bytes: bytes) -> Image.Image | None:
    """
    Converts raw bytes to a PIL object.
    """
    try:
        return Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        logger.debug("Failed to convert bytes to PIL: %s", str(e))
        return None
