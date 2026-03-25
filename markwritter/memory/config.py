"""Configuration for memory service."""

from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class MemoryConfig(BaseModel):
    """Configuration for NoteMemoryService.

    Attributes:
        vault_path: Path to the Obsidian vault
        db_path: Path to the memory database (default: vault_path/.memory/memory.db)
        llm_base_url: Base URL for LLM API
        llm_api_key: API key for LLM (can be set via environment)
        embed_model: Embedding model to use
        chat_model: Chat model to use
        memory_categories: List of memory category names for organizing notes
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vault_path: Path
    db_path: Optional[Path] = None
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    embed_model: str = "nomic-embed-text"
    chat_model: str = "llama3"
    memory_categories: list[str] = Field(
        default_factory=lambda: [
            "concepts",
            "projects",
            "people",
            "resources",
            "daily_notes",
        ]
    )

    def model_post_init(self, _: Any) -> None:
        """Set default db_path if not provided."""
        if self.db_path is None:
            self.db_path = self.vault_path / ".memory" / "memory.db"