"""Database storage backend for non-Markdown content.

This module provides DatabaseRepository, which uses SQLite with aiosqlite
for async operations to store URL, PDF, HTML, and other content types.

Features:
- Full-text search with FTS5
- Vector embeddings for semantic search
- Content deduplication via content_hash
"""

from __future__ import annotations

import hashlib
import json
import logging
import struct
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import aiosqlite

from markwritter.storage.base import StorageError
from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentQuery,
    ContentRef,
    ContentType,
    StorageBackend,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class DatabaseRepository:
    """SQLite-based storage backend for non-Markdown content.

    Supports URL, PDF, HTML, and PLAINTEXT content types with:
    - Async operations via aiosqlite
    - Full-text search via FTS5
    - Vector embeddings for semantic search
    - Content deduplication via hash

    Example:
        >>> repo = DatabaseRepository(db_path=Path("content.db"))
        >>> await repo.initialize()
        >>> content = await repo.get("url-001")
    """

    def __init__(self, db_path: Path | str):
        """Initialize database repository.

        Args:
            db_path: Path to SQLite database file
        """
        self._db_path = Path(db_path)
        self._db: Optional[aiosqlite.Connection] = None

    @property
    def backend_type(self) -> StorageBackend:
        """Return DATABASE backend type."""
        return StorageBackend.DATABASE

    @property
    def supported_content_types(self) -> list[ContentType]:
        """Return supported content types."""
        return [
            ContentType.URL,
            ContentType.PDF,
            ContentType.HTML,
            ContentType.PLAINTEXT,
        ]

    async def initialize(self) -> None:
        """Initialize database tables and indexes.

        Creates:
        - contents: Main content storage
        - contents_fts: FTS5 full-text search index
        - content_vectors: Vector embeddings for semantic search
        """
        # Ensure parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row

        # Enable foreign keys for cascade delete to work
        await self._db.execute("PRAGMA foreign_keys = ON")

        # Create main content table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                storage_backend TEXT NOT NULL DEFAULT 'database',
                text_content TEXT,
                raw_content BLOB,
                title TEXT,
                source_path TEXT,
                source_url TEXT,
                storage_path TEXT,
                metadata JSON,
                tags JSON,
                links JSON,
                backlinks JSON,
                content_hash TEXT UNIQUE,
                mime_type TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                indexed_at TIMESTAMP
            )
        """)

        # Create FTS5 virtual table for full-text search
        await self._db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS contents_fts USING fts5(
                id,
                title,
                text_content,
                tags,
                tokenize='porter unicode61'
            )
        """)

        # Create vector embeddings table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS content_vectors (
                id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                embedding BLOB NOT NULL,
                model TEXT NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        await self._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_contents_source_type
            ON contents(source_type)
        """)

        await self._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_contents_created
            ON contents(created DESC)
        """)

        await self._db.commit()
        logger.info(f"Database initialized at {self._db_path}")

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None

    async def get(self, content_id: str) -> Content | None:
        """Get content by ID.

        Args:
            content_id: Unique identifier for the content

        Returns:
            Content object if found, None otherwise
        """
        if not self._db:
            raise StorageError("Database not initialized")

        cursor = await self._db.execute(
            "SELECT * FROM contents WHERE id = ?",
            (content_id,),
        )
        row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_content(row)

    async def get_by_path(self, path: str) -> Content | None:
        """Get content by storage path.

        Args:
            path: Storage path to search for

        Returns:
            Content object if found, None otherwise
        """
        if not self._db:
            raise StorageError("Database not initialized")

        cursor = await self._db.execute(
            "SELECT * FROM contents WHERE storage_path = ? OR source_path = ?",
            (path, path),
        )
        row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_content(row)

    async def list(self, query: ContentQuery) -> ContentListResult:
        """List content matching query parameters.

        Args:
            query: Query parameters for filtering and pagination

        Returns:
            Paginated result with ContentRef items
        """
        if not self._db:
            raise StorageError("Database not initialized")

        # Build base query
        conditions: list[str] = []
        params: list = []

        # Keyword search via FTS5
        if query.query:
            # Use FTS5 for full-text search
            fts_query = self._sanitize_fts_query(query.query)
            cursor = await self._db.execute(
                """
                SELECT c.* FROM contents c
                JOIN contents_fts fts ON c.id = fts.id
                WHERE contents_fts MATCH ?
                ORDER BY bm25(contents_fts)
                """,
                (fts_query,),
            )
            rows = await cursor.fetchall()

            # Convert to ContentRef and apply other filters
            refs = []
            for row in rows:
                content = self._row_to_content(row)
                if self._matches_filters(content, query):
                    refs.append(content.to_ref())

            # Apply pagination
            total = len(refs)
            paginated_refs = refs[query.offset : query.offset + query.limit]

            return ContentListResult(
                items=paginated_refs,
                total=total,
                limit=query.limit,
                offset=query.offset,
            )

        # Standard query without FTS
        if query.source_types:
            placeholders = ",".join("?" * len(query.source_types))
            conditions.append(f"source_type IN ({placeholders})")
            params.extend([t.value for t in query.source_types])

        if query.storage_backends:
            placeholders = ",".join("?" * len(query.storage_backends))
            conditions.append(f"storage_backend IN ({placeholders})")
            params.extend([b.value for b in query.storage_backends])

        # Build WHERE clause
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM contents {where_clause}"
        cursor = await self._db.execute(count_sql, params)
        total = (await cursor.fetchone())[0]

        # Get paginated results
        sql = f"""
            SELECT * FROM contents
            {where_clause}
            ORDER BY created DESC
            LIMIT ? OFFSET ?
        """
        params.extend([query.limit, query.offset])

        cursor = await self._db.execute(sql, params)
        rows = await cursor.fetchall()

        # Filter by tags if specified (done in Python as JSON array)
        refs = []
        for row in rows:
            content = self._row_to_content(row)
            if query.tags:
                if not any(tag in content.tags for tag in query.tags):
                    continue
            refs.append(content.to_ref())

        # Recalculate total if tag filter was applied
        if query.tags:
            total = len(refs)
            refs = refs[query.offset : query.offset + query.limit]

        return ContentListResult(
            items=refs,
            total=total,
            limit=query.limit,
            offset=query.offset,
        )

    async def save(self, content: Content) -> Content:
        """Save content to database.

        Args:
            content: Content to save

        Returns:
            Saved content object with timestamps set

        Raises:
            StorageError: If content with same hash already exists
        """
        if not self._db:
            raise StorageError("Database not initialized")

        now = datetime.now()

        # Set timestamps
        if content.created is None:
            content.created = now
        content.modified = now

        # Convert lists to JSON
        metadata_json = json.dumps(content.metadata) if content.metadata else None
        tags_json = json.dumps(content.tags) if content.tags else None
        links_json = json.dumps(content.links) if content.links else None
        backlinks_json = json.dumps(content.backlinks) if content.backlinks else None

        try:
            # Check for duplicate content_hash
            if content.content_hash:
                cursor = await self._db.execute(
                    "SELECT id FROM contents WHERE content_hash = ? AND id != ?",
                    (content.content_hash, content.id),
                )
                existing = await cursor.fetchone()
                if existing:
                    raise StorageError(
                        f"Content with hash {content.content_hash} already exists "
                        f"(id: {existing[0]})"
                    )

            # Insert or replace content
            await self._db.execute(
                """
                INSERT OR REPLACE INTO contents (
                    id, source_type, storage_backend, text_content, raw_content,
                    title, source_path, source_url, storage_path, metadata,
                    tags, links, backlinks, content_hash, mime_type,
                    created, modified, indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    content.id,
                    content.source_type.value,
                    content.storage_backend.value,
                    content.text_content,
                    content.raw_content,
                    content.title,
                    content.source_path,
                    content.source_url,
                    content.storage_path,
                    metadata_json,
                    tags_json,
                    links_json,
                    backlinks_json,
                    content.content_hash,
                    content.mime_type,
                    content.created.isoformat() if content.created else None,
                    content.modified.isoformat() if content.modified else None,
                    content.indexed_at.isoformat() if content.indexed_at else None,
                ),
            )

            # Update FTS index
            await self._db.execute(
                """
                INSERT OR REPLACE INTO contents_fts (id, title, text_content, tags)
                VALUES (?, ?, ?, ?)
                """,
                (
                    content.id,
                    content.title or "",
                    content.text_content or "",
                    " ".join(content.tags),
                ),
            )

            await self._db.commit()

        except aiosqlite.IntegrityError as e:
            if "content_hash" in str(e):
                raise StorageError(
                    f"Content with hash {content.content_hash} already exists"
                ) from e
            raise StorageError(f"Failed to save content: {e}") from e

        return content

    async def delete(self, content_id: str) -> bool:
        """Delete content by ID.

        Args:
            content_id: ID of content to delete

        Returns:
            True if deleted, False if not found
        """
        if not self._db:
            raise StorageError("Database not initialized")

        # Check if exists
        if not await self.exists(content_id):
            return False

        # Delete from main table (cascade will handle vectors)
        await self._db.execute(
            "DELETE FROM contents WHERE id = ?",
            (content_id,),
        )

        # Delete from FTS
        await self._db.execute(
            "DELETE FROM contents_fts WHERE id = ?",
            (content_id,),
        )

        await self._db.commit()
        return True

    async def exists(self, content_id: str) -> bool:
        """Check if content exists.

        Args:
            content_id: ID of content to check

        Returns:
            True if content exists, False otherwise
        """
        if not self._db:
            raise StorageError("Database not initialized")

        cursor = await self._db.execute(
            "SELECT 1 FROM contents WHERE id = ?",
            (content_id,),
        )
        row = await cursor.fetchone()
        return row is not None

    # ==============================================================================
    # Vector Operations
    # ==============================================================================

    async def store_vector(
        self,
        content_id: str,
        embedding: Sequence[float],
        model: str,
    ) -> None:
        """Store embedding vector for content.

        Args:
            content_id: ID of content
            embedding: Embedding vector (list of floats)
            model: Name of embedding model used
        """
        if not self._db:
            raise StorageError("Database not initialized")

        # Convert float list to binary blob
        embedding_blob = struct.pack(f"{len(embedding)}f", *embedding)
        vector_id = f"vec_{content_id}"

        await self._db.execute(
            """
            INSERT OR REPLACE INTO content_vectors (id, content_id, embedding, model)
            VALUES (?, ?, ?, ?)
            """,
            (vector_id, content_id, embedding_blob, model),
        )

        await self._db.commit()

    async def get_vector(self, content_id: str) -> Optional[list[float]]:
        """Get embedding vector for content.

        Args:
            content_id: ID of content

        Returns:
            Embedding vector if found, None otherwise
        """
        if not self._db:
            raise StorageError("Database not initialized")

        vector_id = f"vec_{content_id}"

        cursor = await self._db.execute(
            "SELECT embedding FROM content_vectors WHERE id = ?",
            (vector_id,),
        )
        row = await cursor.fetchone()

        if row is None:
            return None

        # Convert binary blob back to float list
        blob = row[0]
        embedding = list(struct.unpack(f"{len(blob) // 4}f", blob))
        return embedding

    async def vector_search(
        self,
        query_embedding: Sequence[float],
        limit: int = 10,
    ) -> list[ContentRef]:
        """Search for similar content using vector similarity.

        Uses cosine similarity approximation for ranking.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum results to return

        Returns:
            List of ContentRef sorted by similarity
        """
        if not self._db:
            raise StorageError("Database not initialized")

        # Get all vectors and compute similarity
        cursor = await self._db.execute(
            "SELECT content_id, embedding FROM content_vectors"
        )
        rows = await cursor.fetchall()

        similarities: list[tuple[str, float]] = []
        query_vec = list(query_embedding)
        query_norm = sum(x * x for x in query_vec) ** 0.5

        for row in rows:
            content_id = row[0]
            blob = row[1]
            stored_vec = list(struct.unpack(f"{len(blob) // 4}f", blob))

            # Compute cosine similarity
            stored_norm = sum(x * x for x in stored_vec) ** 0.5
            if stored_norm == 0 or query_norm == 0:
                continue

            dot_product = sum(a * b for a, b in zip(query_vec, stored_vec))
            similarity = dot_product / (query_norm * stored_norm)

            similarities.append((content_id, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top results
        results: list[ContentRef] = []
        for content_id, _ in similarities[:limit]:
            content = await self.get(content_id)
            if content:
                results.append(content.to_ref())

        return results

    # ==============================================================================
    # Private Helpers
    # ==============================================================================

    def _row_to_content(self, row: aiosqlite.Row) -> Content:
        """Convert database row to Content object.

        Args:
            row: Database row

        Returns:
            Content object
        """
        # Parse JSON fields
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        tags = json.loads(row["tags"]) if row["tags"] else []
        links = json.loads(row["links"]) if row["links"] else []
        backlinks = json.loads(row["backlinks"]) if row["backlinks"] else []

        # Parse timestamps
        created = (
            datetime.fromisoformat(row["created"]) if row["created"] else None
        )
        modified = (
            datetime.fromisoformat(row["modified"]) if row["modified"] else None
        )
        indexed_at = (
            datetime.fromisoformat(row["indexed_at"]) if row["indexed_at"] else None
        )

        return Content(
            id=row["id"],
            source_type=ContentType(row["source_type"]),
            storage_backend=StorageBackend(row["storage_backend"]),
            text_content=row["text_content"],
            raw_content=row["raw_content"],
            title=row["title"],
            source_path=row["source_path"],
            source_url=row["source_url"],
            storage_path=row["storage_path"],
            metadata=metadata,
            tags=tags,
            links=links,
            backlinks=backlinks,
            content_hash=row["content_hash"],
            mime_type=row["mime_type"],
            created=created,
            modified=modified,
            indexed_at=indexed_at,
        )

    def _sanitize_fts_query(self, query: str) -> str:
        """Sanitize query for FTS5.

        Args:
            query: Raw query string

        Returns:
            Sanitized FTS5 query
        """
        # Remove special FTS5 characters
        import re

        sanitized = re.sub(r"[^\w\s\*]", " ", query)

        # Split into terms
        terms = sanitized.split()

        if not terms:
            return ""

        # Join with OR for broader matching
        return " OR ".join(terms)

    def _matches_filters(self, content: Content, query: ContentQuery) -> bool:
        """Check if content matches query filters.

        Args:
            content: Content to check
            query: Query with filters

        Returns:
            True if content matches all filters
        """
        if query.source_types and content.source_type not in query.source_types:
            return False

        if query.storage_backends:
            if content.storage_backend not in query.storage_backends:
                return False

        if query.tags:
            if not any(tag in content.tags for tag in query.tags):
                return False

        return True


__all__ = ["DatabaseRepository"]