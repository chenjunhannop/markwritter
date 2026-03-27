"""Storage abstraction layer for Markwritter.

This module provides a unified interface for content storage,
supporting multiple backends (Obsidian, databases, object stores).

Usage:
    from markwritter.storage import ContentRepository, Content, ContentQuery
    from markwritter.storage.backends.obsidian import ObsidianRepository

    # Create repository
    repo = ObsidianRepository(vault_path="/path/to/vault")

    # Get content
    content = await repo.get("note.md")

    # List content
    result = await repo.list(ContentQuery(tags=["python"]))
"""

from markwritter.storage.base import (
    ContentNotFoundError,
    ContentRepository,
    StorageError,
)
from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentQuery,
    ContentRef,
    ContentType,
    StorageBackend,
)
from markwritter.storage.registry import StorageRegistry
from markwritter.storage.service import ContentService
from markwritter.storage.ingestion import ContentIngestResult, IngestionPipeline

__all__ = [
    # Models
    "ContentType",
    "StorageBackend",
    "ContentRef",
    "Content",
    "ContentQuery",
    "ContentListResult",
    # Protocol
    "ContentRepository",
    # Exceptions
    "StorageError",
    "ContentNotFoundError",
    # Registry
    "StorageRegistry",
    # Service
    "ContentService",
    # Ingestion
    "ContentIngestResult",
    "IngestionPipeline",
]
