"""Query module for Markwritter.

Provides keyword search, semantic search, and Q&A functionality.
"""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Optional,
    Protocol,
)

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from markwritter.obsidian.vault import ObsidianVault

logger = logging.getLogger(__name__)


# ==============================================================================
# Data Models
# ==============================================================================


class SearchResult(BaseModel):
    """Model for a single search result."""

    note_path: str
    title: str
    score: float
    snippet: str


class HighlightResult(BaseModel):
    """Model for a search result with highlighted snippet."""

    note_path: str
    title: str
    score: float
    highlighted_snippet: str


class HybridSearchResult(BaseModel):
    """Model for hybrid search result with combined scores."""

    note_path: str
    title: str
    semantic_score: float
    keyword_score: float
    combined_score: float
    snippet: str


class SourceReference(BaseModel):
    """Model for a source reference in Q&A."""

    note_path: str
    title: str
    relevance_score: float = 0.0
    snippet: str = ""


class AnswerResult(BaseModel):
    """Model for Q&A answer."""

    question: str
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)


# ==============================================================================
# Protocols
# ==============================================================================


class MemoryServiceProtocol(Protocol):
    """Protocol for memory service interface."""

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Retrieve relevant memories."""
        ...


class LLMClientProtocol(Protocol):
    """Protocol for LLM client interface."""

    async def generate(
        self,
        prompt: str,
        *,
        context: Optional[list[dict[str, str]]] = None,
    ) -> str:
        """Generate text from prompt."""
        ...

    async def stream_generate(
        self,
        prompt: str,
        *,
        context: Optional[list[dict[str, str]]] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream generate text from prompt."""
        ...


# ==============================================================================
# Keyword Search (SQLite FTS5)
# ==============================================================================


class KeywordSearch:
    """Keyword search using SQLite FTS5.

    Provides full-text search capabilities for note content.

    Example:
        >>> search = KeywordSearch(db_path=Path("search.db"))
        >>> search.index_note("note.md", "Title", "Content", ["tag"])
        >>> results = search.search("content")
    """

    def __init__(self, db_path: Path | str):
        """Initialize keyword search.

        Args:
            db_path: Path to SQLite database file
        """
        self._db_path = Path(db_path)
        self._init_database()

    @property
    def db_path(self) -> Path:
        """Return database path."""
        return self._db_path

    def _init_database(self) -> None:
        """Initialize FTS5 tables."""
        # Ensure parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        # Create FTS5 virtual table for notes
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
                note_path,
                title,
                content,
                tags,
                tokenize='porter unicode61'
            )
        """)

        # Create metadata table for tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes_meta (
                note_path TEXT PRIMARY KEY,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self._db_path)

    def index_note(
        self,
        note_path: str,
        title: str,
        content: str,
        tags: list[str],
    ) -> bool:
        """Index a note for search.

        Args:
            note_path: Path to the note
            title: Note title
            content: Note content
            tags: List of tags

        Returns:
            True if indexing successful
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Delete existing entry if any
            cursor.execute(
                "DELETE FROM notes_fts WHERE note_path = ?",
                (note_path,),
            )

            # Insert new entry
            tags_str = " ".join(tags)
            cursor.execute(
                """
                INSERT INTO notes_fts (note_path, title, content, tags)
                VALUES (?, ?, ?, ?)
                """,
                (note_path, title, content, tags_str),
            )

            # Update metadata
            cursor.execute(
                """
                INSERT OR REPLACE INTO notes_meta (note_path)
                VALUES (?)
                """,
                (note_path,),
            )

            conn.commit()
            return True

        except Exception as e:
            logger.error(f"Error indexing note {note_path}: {e}")
            conn.rollback()
            return False

        finally:
            conn.close()

    def remove_note(self, note_path: str) -> bool:
        """Remove a note from the index.

        Args:
            note_path: Path to the note

        Returns:
            True if removal successful, False if note not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM notes_fts WHERE note_path = ?",
                (note_path,),
            )

            deleted = cursor.rowcount > 0

            if deleted:
                cursor.execute(
                    "DELETE FROM notes_meta WHERE note_path = ?",
                    (note_path,),
                )

            conn.commit()
            return deleted

        except Exception as e:
            logger.error(f"Error removing note {note_path}: {e}")
            conn.rollback()
            return False

        finally:
            conn.close()

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Search for notes matching query.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        if not query or not query.strip():
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Sanitize query for FTS5
            fts_query = self._sanitize_fts_query(query)

            # Execute FTS5 search with BM25 ranking
            cursor.execute(
                """
                SELECT
                    note_path,
                    title,
                    bm25(notes_fts) as score,
                    snippet(notes_fts, 2, '...', '...', 50, 3) as snippet
                FROM notes_fts
                WHERE notes_fts MATCH ?
                ORDER BY score ASC
                LIMIT ?
                """,
                (fts_query, limit),
            )

            results = []
            for row in cursor.fetchall():
                note_path, title, score, snippet = row
                # BM25 returns negative scores (lower is better), negate for display
                results.append(SearchResult(
                    note_path=note_path,
                    title=title,
                    score=-score if score < 0 else score,
                    snippet=snippet or "",
                ))

            return results

        except sqlite3.OperationalError as e:
            logger.warning(f"FTS query error: {e}")
            return []

        finally:
            conn.close()

    def search_with_highlight(
        self,
        query: str,
        limit: int = 10,
    ) -> list[HighlightResult]:
        """Search with highlighted snippets.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of HighlightResult objects
        """
        if not query or not query.strip():
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            fts_query = self._sanitize_fts_query(query)

            # Use highlight function for <mark> tags
            cursor.execute(
                """
                SELECT
                    note_path,
                    title,
                    bm25(notes_fts) as score,
                    highlight(notes_fts, 2, '<mark>', '</mark>') as highlighted
                FROM notes_fts
                WHERE notes_fts MATCH ?
                ORDER BY score ASC
                LIMIT ?
                """,
                (fts_query, limit),
            )

            results = []
            for row in cursor.fetchall():
                note_path, title, score, highlighted = row
                results.append(HighlightResult(
                    note_path=note_path,
                    title=title,
                    score=-score if score < 0 else score,
                    highlighted_snippet=highlighted or "",
                ))

            return results

        except sqlite3.OperationalError as e:
            logger.warning(f"FTS query error: {e}")
            return []

        finally:
            conn.close()

    def _sanitize_fts_query(self, query: str) -> str:
        """Sanitize query for FTS5.

        Args:
            query: Raw query string

        Returns:
            Sanitized FTS5 query
        """
        # Remove special FTS5 characters that could cause issues
        # Keep alphanumeric, spaces, and asterisk for prefix matching
        sanitized = re.sub(r'[^\w\s\*]', ' ', query)

        # Split into terms and join with OR for broader matching
        terms = sanitized.split()

        if not terms:
            return ""

        # For simple queries, just join terms
        # For phrase matching, keep quotes
        if '"' in query:
            # Preserve phrase queries
            return query

        # Convert to OR query for broader matching
        return " OR ".join(terms)

    def clear_index(self) -> bool:
        """Clear all indexed content.

        Returns:
            True if successful
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM notes_fts")
            cursor.execute("DELETE FROM notes_meta")
            conn.commit()
            return True

        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            conn.rollback()
            return False

        finally:
            conn.close()

    def get_indexed_count(self) -> int:
        """Get count of indexed notes.

        Returns:
            Number of indexed notes
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM notes_meta")
            count = cursor.fetchone()[0]
            return count

        finally:
            conn.close()


# ==============================================================================
# Semantic Search
# ==============================================================================


class SemanticSearch:
    """Semantic search using memory service.

    Provides vector-based semantic search capabilities.

    Example:
        >>> search = SemanticSearch(memory_service=service, vault=vault)
        >>> results = await search.search("python testing")
    """

    def __init__(
        self,
        memory_service: MemoryServiceProtocol,
        vault: Optional[ObsidianVault] = None,
        keyword_search: Optional[KeywordSearch] = None,
    ):
        """Initialize semantic search.

        Args:
            memory_service: Memory service for vector search
            vault: Optional Obsidian vault for note retrieval
            keyword_search: Optional keyword search for hybrid mode
        """
        self._memory_service = memory_service
        self._vault = vault
        self._keyword_search = keyword_search

    @property
    def memory_service(self) -> MemoryServiceProtocol:
        """Return memory service."""
        return self._memory_service

    @property
    def vault(self) -> Optional[ObsidianVault]:
        """Return vault."""
        return self._vault

    async def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Search for notes using semantic similarity.

        Args:
            query: Search query
            top_k: Maximum results

        Returns:
            List of SearchResult objects
        """
        if not query or not query.strip():
            return []

        try:
            result = await self._memory_service.retrieve(query, top_k=top_k)

            results: list[SearchResult] = []

            for item in result.get("items", []):
                note_path = item.get("user", {}).get("note_path", "")
                if not note_path:
                    continue

                # Get note details from vault if available
                title = note_path
                snippet = item.get("content", "")[:200]

                if self._vault:
                    try:
                        note = self._vault.read_note(note_path)
                        title = note.title or note_path
                        snippet = self._get_snippet(note.content, query)
                    except Exception:
                        # Note might not exist anymore
                        continue

                results.append(SearchResult(
                    note_path=note_path,
                    title=title,
                    score=item.get("score", 0.0),
                    snippet=snippet,
                ))

            return results

        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []

    def _get_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Get content snippet relevant to query.

        Args:
            content: Full content
            query: Search query
            max_length: Maximum snippet length

        Returns:
            Content snippet
        """
        query_lower = query.lower()
        content_lower = content.lower()

        pos = content_lower.find(query_lower.split()[0] if query_lower else "")

        if pos == -1:
            return content[:max_length] + "..." if len(content) > max_length else content

        context_before = min(50, max_length // 3)
        context_after = max_length - context_before

        start = max(0, pos - context_before)
        end = min(len(content), pos + context_after)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    async def hybrid_search(
        self,
        query: str,
        mode: str = "balanced",
        top_k: int = 5,
    ) -> list[HybridSearchResult]:
        """Hybrid search combining keyword and semantic.

        Args:
            query: Search query
            mode: Search mode - "keyword", "semantic", or "balanced"
            top_k: Maximum results

        Returns:
            List of HybridSearchResult objects
        """
        if mode == "keyword":
            # Keyword-only mode
            if not self._keyword_search:
                return []
            kw_results = self._keyword_search.search(query, limit=top_k)
            return [
                HybridSearchResult(
                    note_path=r.note_path,
                    title=r.title,
                    semantic_score=0.0,
                    keyword_score=r.score,
                    combined_score=r.score,
                    snippet=r.snippet,
                )
                for r in kw_results
            ]

        if mode == "semantic":
            # Semantic-only mode
            sem_results = await self.search(query, top_k=top_k)
            return [
                HybridSearchResult(
                    note_path=r.note_path,
                    title=r.title,
                    semantic_score=r.score,
                    keyword_score=0.0,
                    combined_score=r.score,
                    snippet=r.snippet,
                )
                for r in sem_results
            ]

        # Balanced mode: combine both
        keyword_weight = 0.4
        semantic_weight = 0.6

        results_map: dict[str, HybridSearchResult] = {}

        # Get keyword results
        if self._keyword_search:
            kw_results = self._keyword_search.search(query, limit=top_k * 2)
            max_kw_score = max((r.score for r in kw_results), default=1.0)

            for r in kw_results:
                normalized_score = r.score / max_kw_score if max_kw_score > 0 else 0
                results_map[r.note_path] = HybridSearchResult(
                    note_path=r.note_path,
                    title=r.title,
                    semantic_score=0.0,
                    keyword_score=normalized_score,
                    combined_score=normalized_score * keyword_weight,
                    snippet=r.snippet,
                )

        # Get semantic results
        sem_results = await self.search(query, top_k=top_k * 2)
        max_sem_score = max((r.score for r in sem_results), default=1.0)

        for r in sem_results:
            normalized_score = r.score / max_sem_score if max_sem_score > 0 else 0

            if r.note_path in results_map:
                # Update existing
                existing = results_map[r.note_path]
                results_map[r.note_path] = HybridSearchResult(
                    note_path=r.note_path,
                    title=r.title,
                    semantic_score=normalized_score,
                    keyword_score=existing.keyword_score,
                    combined_score=(
                        existing.keyword_score * keyword_weight +
                        normalized_score * semantic_weight
                    ),
                    snippet=r.snippet,
                )
            else:
                results_map[r.note_path] = HybridSearchResult(
                    note_path=r.note_path,
                    title=r.title,
                    semantic_score=normalized_score,
                    keyword_score=0.0,
                    combined_score=normalized_score * semantic_weight,
                    snippet=r.snippet,
                )

        # Sort by combined score
        results = sorted(
            results_map.values(),
            key=lambda x: x.combined_score,
            reverse=True,
        )

        return results[:top_k]

    def _keyword_search(self, query: str) -> list[SearchResult]:
        """Internal keyword search method."""
        if self._keyword_search:
            return self._keyword_search.search(query)
        return []


# ==============================================================================
# Q&A System
# ==============================================================================


class QASystem:
    """Intelligent Q&A system using RAG.

    Provides question answering capabilities based on indexed notes.

    Example:
        >>> qa = QASystem(memory_service=service, vault=vault)
        >>> result = await qa.ask("What is Python testing?")
    """

    def __init__(
        self,
        memory_service: MemoryServiceProtocol,
        vault: Optional[ObsidianVault] = None,
        llm_client: Optional[LLMClientProtocol] = None,
    ):
        """Initialize Q&A system.

        Args:
            memory_service: Memory service for retrieval
            vault: Optional Obsidian vault for note retrieval
            llm_client: Optional LLM client for generation
        """
        self._memory_service = memory_service
        self._vault = vault
        self._llm_client = llm_client

    @property
    def memory_service(self) -> MemoryServiceProtocol:
        """Return memory service."""
        return self._memory_service

    @property
    def vault(self) -> Optional[ObsidianVault]:
        """Return vault."""
        return self._vault

    @property
    def llm_client(self) -> Optional[LLMClientProtocol]:
        """Return LLM client."""
        return self._llm_client

    async def ask(
        self,
        question: str,
        top_k: int = 5,
        context: Optional[list[dict[str, str]]] = None,
    ) -> AnswerResult:
        """Ask a question based on indexed notes.

        Args:
            question: Question to answer
            top_k: Number of sources to retrieve
            context: Optional conversation context

        Returns:
            AnswerResult with answer and sources
        """
        if not question or not question.strip():
            return AnswerResult(
                question=question,
                answer="Please provide a question.",
                sources=[],
            )

        try:
            # Retrieve relevant notes
            retrieve_result = await self._memory_service.retrieve(
                question,
                top_k=top_k,
            )

            items = retrieve_result.get("items", [])

            if not items:
                return AnswerResult(
                    question=question,
                    answer="I couldn't find any relevant notes to answer your question.",
                    sources=[],
                )

            # Build sources
            sources: list[SourceReference] = []
            context_parts: list[str] = []

            for item in items:
                note_path = item.get("user", {}).get("note_path", "")
                if not note_path:
                    continue

                # Get note details
                title = note_path
                content = item.get("content", "")

                if self._vault:
                    try:
                        note = self._vault.read_note(note_path)
                        title = note.title or note_path
                        content = note.content
                    except Exception:
                        continue

                sources.append(SourceReference(
                    note_path=note_path,
                    title=title,
                    relevance_score=item.get("score", 0.0),
                    snippet=content[:200],
                ))

                context_parts.append(f"## {title}\n\n{content}")

            if not sources:
                return AnswerResult(
                    question=question,
                    answer="I found references but couldn't access the source notes.",
                    sources=[],
                )

            # Generate answer
            answer = await self._generate_answer(
                question,
                context_parts,
                context=context,
            )

            return AnswerResult(
                question=question,
                answer=answer,
                sources=sources,
            )

        except Exception as e:
            logger.error(f"Q&A error: {e}")
            return AnswerResult(
                question=question,
                answer="An error occurred while processing your question.",
                sources=[],
            )

    async def _generate_answer(
        self,
        question: str,
        context_parts: list[str],
        context: Optional[list[dict[str, str]]] = None,
    ) -> str:
        """Generate answer from context.

        Args:
            question: Question to answer
            context_parts: Context parts from retrieved notes
            context: Optional conversation context

        Returns:
            Generated answer
        """
        if self._llm_client:
            try:
                context_text = "\n\n---\n\n".join(context_parts)

                prompt = f"""Based on the following notes, answer the question.
If the answer is not in the notes, say so.

Notes:
{context_text}

Question: {question}

Answer:"""

                return await self._llm_client.generate(prompt, context=context)

            except Exception as e:
                logger.error(f"LLM generation error: {e}")

        # Fallback: return context summary
        if context_parts:
            return f"Based on your notes: {context_parts[0][:200]}..."
        return "No context available."

    async def ask_stream(
        self,
        question: str,
        top_k: int = 5,
        context: Optional[list[dict[str, str]]] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Ask a question with streaming response.

        Args:
            question: Question to answer
            top_k: Number of sources to retrieve
            context: Optional conversation context

        Yields:
            Dict with streaming chunks
        """
        if not question or not question.strip():
            yield {"type": "error", "content": "Please provide a question."}
            return

        try:
            # Retrieve relevant notes
            retrieve_result = await self._memory_service.retrieve(
                question,
                top_k=top_k,
            )

            items = retrieve_result.get("items", [])

            if not items:
                yield {"type": "token", "content": "I couldn't find any relevant notes."}
                yield {"type": "sources", "content": []}
                yield {"type": "done"}
                return

            # Build sources
            sources: list[dict[str, Any]] = []

            for item in items:
                note_path = item.get("user", {}).get("note_path", "")
                if not note_path:
                    continue

                title = note_path
                if self._vault:
                    try:
                        note = self._vault.read_note(note_path)
                        title = note.title or note_path
                    except Exception:
                        pass

                sources.append({
                    "note_path": note_path,
                    "title": title,
                    "relevance_score": item.get("score", 0.0),
                })

            # Stream answer
            async for chunk in self._stream_answer(
                question,
                items,
                context=context,
            ):
                yield chunk

            # Send sources
            yield {"type": "sources", "content": sources}
            yield {"type": "done"}

        except Exception as e:
            logger.error(f"Streaming Q&A error: {e}")
            yield {"type": "error", "content": str(e)}

    async def _stream_answer(
        self,
        question: str,
        items: list[dict[str, Any]],
        context: Optional[list[dict[str, str]]] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream answer generation.

        Args:
            question: Question to answer
            items: Retrieved items
            context: Optional conversation context

        Yields:
            Dict with streaming chunks
        """
        if self._llm_client:
            try:
                # Build context
                context_parts = []
                for item in items:
                    content = item.get("content", "")
                    note_path = item.get("user", {}).get("note_path", "")
                    if self._vault:
                        try:
                            note = self._vault.read_note(note_path)
                            content = note.content
                        except Exception:
                            pass
                    context_parts.append(content)

                context_text = "\n\n---\n\n".join(context_parts)

                prompt = f"""Based on the following notes, answer the question.

Notes:
{context_text}

Question: {question}

Answer:"""

                # Stream generation
                async for token in self._llm_client.stream_generate(prompt, context=context):
                    yield {"type": "token", "content": token}

                return

            except Exception as e:
                logger.error(f"Streaming generation error: {e}")
                yield {"type": "error", "content": str(e)}
                return

        # Fallback: yield simple response
        yield {"type": "token", "content": "Based on your notes, "}
        for item in items[:1]:
            content = item.get("content", "")[:100]
            yield {"type": "token", "content": content}
        yield {"type": "token", "content": "..."}
