"""Storage backends for Markwritter.

This package contains implementations of ContentRepository
for different storage systems.
"""

from markwritter.storage.backends.database import DatabaseRepository
from markwritter.storage.backends.obsidian import ObsidianRepository

__all__ = [
    "DatabaseRepository",
    "ObsidianRepository",
]
