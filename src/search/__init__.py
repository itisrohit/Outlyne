"""
Outlyne Search Module

Contains search adapters and utilities for the Recall Engine.
Includes DuckDuckGo integration and thumbnail downloading.
"""

from .base import BaseSearchAdapter
from .ddg import DuckDuckGoAdapter

__all__ = ["BaseSearchAdapter", "DuckDuckGoAdapter"]
