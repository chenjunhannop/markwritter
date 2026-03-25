"""Memory service integration with memU.

This module provides NoteMemoryService that wraps memU's MemoryService
to provide semantic indexing and search for Obsidian notes.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Protocol

from markwritter.memory.config import MemoryConfig
from markwritter.obsidian.vault import ObsidianVault

if TYPE_CHECKING:
    from memu.app.service import MemoryService

logger = logging.getLogger(__name__)


class MemoryServiceProtocol(Protocol):
    """Protocol for memU MemoryService interface."""

    async def memorize(
        self,
        content: str,
        *,
        user: dict[str, Any] | None = None,
        categories: list[str] | None = None,
    ) -> dict[str, Any]:
        """Store content in memory."""
        ...

    async def retrieve(
        self,
        query: str,
        *,
        user: dict[str, Any] | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Retrieve relevant memories."""
        ...

    async def list_memory_items(
        self,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """List memory items."""
        ...

    async def create_memory_item(
        self,
        *,
        memory_type: str,
        memory_content: str,
        memory_categories: list[str],
        user: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a memory item."""
        ...

    async def clear_memory(
        self,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Clear memory items."""
        ...


class NoteMemoryService:
    """Service for indexing and searching Obsidian notes using memU.

    This service wraps memU's MemoryService to provide:
    - Semantic indexing of note content
    - Vector-based search across notes
    - Intelligent Q&A over note content

    Example:
        >>> config = MemoryConfig(vault_path=Path("/path/to/vault"))
        >>> service = NoteMemoryService(config)
        >>> await service.index_vault()
        >>> results = await service.search("python testing")
    """

    def __init__(
        self,
        config: MemoryConfig,
        *,
        vault: Optional[ObsidianVault] = None,
        memory_service: Optional[MemoryServiceProtocol] = None,
    ):
        """Initialize the note memory service.

        Args:
            config: Memory service configuration
            vault: Optional ObsidianVault instance (created from config if not provided)
            memory_service: Optional memU MemoryService (created if not provided)
        """
        self._config = config
        self._vault = vault or ObsidianVault(config.vault_path)
        self._memory_service: Optional[MemoryServiceProtocol] = memory_service
        self._initialized = False

    @property
    def config(self) -> MemoryConfig:
        """Return the configuration."""
        return self._config

    @property
    def vault(self) -> ObsidianVault:
        """Return the Obsidian vault."""
        return self._vault

    @property
    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._initialized

    def _get_memory_service(self) -> MemoryServiceProtocol:
        """Get or create the memU MemoryService.

        Returns:
            The memU MemoryService instance

        Raises:
            ImportError: If memU is not installed
            ValueError: If the memory service is not configured
        """
        if self._memory_service is None:
            try:
                from memu import MemoryService as MemUService

                # Build memU configuration
                memu_config = self._build_memu_config()
                self._memory_service = MemUService(**memu_config)
            except ImportError as e:
                raise ImportError(
                    "memU is not installed. Install it with: pip install memu"
                ) from e
        return self._memory_service

    def _build_memu_config(self) -> dict[str, Any]:
        """Build memU configuration from MemoryConfig.

        Returns:
            Configuration dict for memU MemoryService
        """
        # Ensure db directory exists
        if self._config.db_path:
            self._config.db_path.parent.mkdir(parents=True, exist_ok=True)

        return {
            "llm_profiles": {
                "default": {
                    "base_url": self._config.llm_base_url,
                    "api_key": self._config.llm_api_key,
                    "chat_model": self._config.chat_model,
                },
                "embedding": {
                    "base_url": self._config.llm_base_url,
                    "api_key": self._config.llm_api_key,
                    "embed_model": self._config.embed_model,
                },
            },
            "database_config": {
                "metadata_store": {
                    "provider": "sqlite",
                    "db_path": str(self._config.db_path),
                },
                "vector_index": {
                    "provider": "sqlite",
                },
            },
            "memorize_config": {
                "memory_categories": [
                    {"name": cat, "description": f"Notes about {cat}"}
                    for cat in self._config.memory_categories
                ],
            },
        }

    async def initialize(self) -> None:
        """Initialize the memory service.

        This ensures the database and LLM connections are ready.
        """
        self._get_memory_service()
        self._initialized = True
        logger.info(
            f"NoteMemoryService initialized for vault: {self._config.vault_path}"
        )

    async def index_vault(
        self,
        *,
        batch_size: int = 10,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Index all notes in the vault.

        Args:
            batch_size: Number of notes to process at once
            overwrite: Whether to re-index existing notes

        Returns:
            Dict with indexing results:
                - indexed: Number of notes indexed
                - skipped: Number of notes skipped
                - errors: List of error messages
        """
        if not self._initialized:
            await self.initialize()

        if overwrite:
            await self.clear_index()

        notes = self._vault.list_notes()
        indexed = 0
        skipped = 0
        errors: list[str] = []

        service = self._get_memory_service()

        for note_meta in notes:
            try:
                # Read full note content
                note = self._vault.read_note(note_meta.path)

                # Build content for indexing
                content = self._build_indexable_content(note)

                # Determine category from note path/tags
                category = self._determine_category(note)

                # Index the note
                await service.create_memory_item(
                    memory_type="note",
                    memory_content=content,
                    memory_categories=[category],
                    user={"note_path": note.path},
                )
                indexed += 1

            except Exception as e:
                errors.append(f"Error indexing {note_meta.path}: {str(e)}")
                logger.error(f"Error indexing {note_meta.path}: {e}")

        return {
            "indexed": indexed,
            "skipped": skipped,
            "errors": errors,
        }

    async def index_note(self, note_path: str) -> dict[str, Any]:
        """Index a single note.

        Args:
            note_path: Path to the note (relative to vault root)

        Returns:
            Dict with indexing result

        Raises:
            NoteNotFoundError: If note doesn't exist
        """
        if not self._initialized:
            await self.initialize()

        note = self._vault.read_note(note_path)
        content = self._build_indexable_content(note)
        category = self._determine_category(note)

        service = self._get_memory_service()
        result = await service.create_memory_item(
            memory_type="note",
            memory_content=content,
            memory_categories=[category],
            user={"note_path": note.path},
        )

        return {
            "indexed": 1,
            "note_path": note_path,
            "category": category,
            "result": result,
        }

    async def search(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Search for notes using semantic search.

        Args:
            query: Search query
            top_k: Maximum number of results

        Returns:
            List of search results, each containing:
                - note_path: Path to the note
                - title: Note title
                - score: Relevance score
                - snippet: Content snippet
        """
        if not self._initialized:
            await self.initialize()

        service = self._get_memory_service()
        result = await service.retrieve(query, top_k=top_k)

        # Transform results to note format
        results: list[dict[str, Any]] = []
        for item in result.get("items", []):
            note_path = item.get("user", {}).get("note_path", "")
            if note_path:
                try:
                    note = self._vault.read_note(note_path)
                    results.append({
                        "note_path": note_path,
                        "title": note.title,
                        "score": item.get("score", 0.0),
                        "snippet": self._get_snippet(note.content, query),
                    })
                except Exception:
                    # Skip if note no longer exists
                    continue

        return results

    async def ask(self, question: str) -> dict[str, Any]:
        """Ask a question about the notes.

        This uses RAG to answer questions based on indexed note content.

        Args:
            question: Question to answer

        Returns:
            Dict containing:
                - answer: Generated answer
                - sources: List of source notes used
        """
        if not self._initialized:
            await self.initialize()

        # Retrieve relevant notes
        results = await self.search(question, top_k=5)

        if not results:
            return {
                "answer": "I couldn't find any relevant notes to answer your question.",
                "sources": [],
            }

        # Build context from search results
        context_parts = []
        sources = []
        for result in results:
            note = self._vault.read_note(result["note_path"])
            context_parts.append(f"## {note.title}\n\n{note.content}")
            sources.append({
                "note_path": result["note_path"],
                "title": result["title"],
            })

        # Use memU's LLM for answering
        service = self._get_memory_service()
        context = "\n\n---\n\n".join(context_parts)

        # Use the LLM client directly for Q&A
        prompt = f"""Based on the following notes, answer the question.

Notes:
{context}

Question: {question}

Answer:"""

        # This is a simplified version - in production, use memU's full RAG pipeline
        response = await service.retrieve(question, top_k=3)

        return {
            "answer": response.get("answer", "Unable to generate answer."),
            "sources": sources,
        }

    async def clear_index(self) -> dict[str, Any]:
        """Clear all indexed notes from memory.

        Returns:
            Dict with clear results
        """
        if not self._initialized:
            await self.initialize()

        service = self._get_memory_service()
        result = await service.clear_memory()

        return {
            "cleared": True,
            "result": result,
        }

    def _build_indexable_content(self, note: Any) -> str:
        """Build content string for indexing.

        Args:
            note: Note object

        Returns:
            Content string including title, metadata, and body
        """
        parts = [f"# {note.title}"]

        # Add tags if present
        tags = note.metadata.get("tags", [])
        if tags:
            parts.append(f"\nTags: {', '.join(tags)}")

        # Add content
        parts.append(f"\n{note.content}")

        return "\n".join(parts)

    def _determine_category(self, note: Any) -> str:
        """Determine memory category for a note.

        Args:
            note: Note object

        Returns:
            Category name
        """
        # Check path-based categories
        path_lower = note.path.lower()

        if "daily" in path_lower or "journal" in path_lower:
            return "daily_notes"
        if "project" in path_lower:
            return "projects"
        if "person" in path_lower or "people" in path_lower:
            return "people"
        if "resource" in path_lower or "reference" in path_lower:
            return "resources"

        # Check tags
        tags = note.metadata.get("tags", [])
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in self._config.memory_categories:
                return tag_lower

        # Default to concepts
        return "concepts"

    def _get_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Get a content snippet relevant to the query.

        Args:
            content: Full content
            query: Search query
            max_length: Maximum snippet length

        Returns:
            Content snippet
        """
        # Find query position
        query_lower = query.lower()
        content_lower = content.lower()

        pos = content_lower.find(query_lower)
        if pos == -1:
            # Return beginning if query not found
            return content[:max_length] + "..." if len(content) > max_length else content

        # Extract snippet around the query
        # Calculate context before and after the query
        context_before = min(50, max_length // 3)
        context_after = max_length - context_before - len(query)

        start = max(0, pos - context_before)
        end = min(len(content), pos + len(query) + context_after)

        # Ensure we have at least some content
        if end <= start:
            end = min(len(content), start + max_length)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet