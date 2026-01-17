from abc import ABC, abstractmethod
from typing import Any


class BaseSearchAdapter(ABC):
    """
    Abstract base class for image search adapters.
    """

    @abstractmethod
    async def search(self, query: str, max_results: int = 50) -> list[dict[str, Any]]:
        """
        Perform an image search and return a list of results.

        Args:
            query: The search query string.
            max_results: Maximum number of results to return.

        Returns:
            A list of dicts, each containing 'url', 'thumbnail', and 'title'.
        """
        pass
