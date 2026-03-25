"""Memory service integration with memU.

This module provides NoteMemoryService for indexing and searching Obsidian notes
using memU's semantic memory capabilities.
"""

from markwritter.memory.service import NoteMemoryService
from markwritter.memory.config import MemoryConfig

__all__ = ["NoteMemoryService", "MemoryConfig"]