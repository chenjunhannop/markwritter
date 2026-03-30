"""Chat session database management.

This module provides ChatSessionDB, which manages persistent storage for chat sessions.
Sessions track selected sources and conversation history across requests.

Features:
- Session persistence across page refreshes
- Selected source tracking (file paths)
- Conversation history storage
- Automatic cleanup of expired sessions
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import aiosqlite

logger = logging.getLogger(__name__)


class ChatSessionDB:
    """SQLite database for chat session persistence.

    Stores:
    - session_id → selected_source_paths mapping
    - Conversation history
    - Session metadata (created_at, last_accessed)

    Example:
        >>> db = ChatSessionDB(db_path=Path("chat_sessions.db"))
        >>> await db.initialize()
        >>> await db.save_session("session-123", ["notes/a.md", "notes/b.md"])
        >>> sources = await db.get_sources("session-123")
    """

    def __init__(self, db_path: Path | str):
        """Initialize chat session database.

        Args:
            db_path: Path to SQLite database file
        """
        self._db_path = Path(db_path)
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """Initialize database tables.

        Creates:
        - chat_sessions: Session metadata and selected sources
        - conversation_history: Message history per session
        """
        # Ensure parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row

        # Create chat_sessions table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                selected_source_paths TEXT NOT NULL DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create conversation_history table
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_index INTEGER NOT NULL,
                role TEXT NOT NULL,  -- 'user' or 'assistant'
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
                    ON DELETE CASCADE,
                UNIQUE (session_id, message_index)
            )
        """)

        # Create index for faster session lookups
        await self._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversation_session
            ON conversation_history(session_id, message_index)
        """)

        await self._db.commit()
        logger.info(f"Initialized chat session database: {self._db_path}")

    async def save_session(
        self,
        session_id: str,
        selected_source_paths: list[str],
    ) -> None:
        """Save or update session with selected sources.

        Args:
            session_id: Unique session identifier
            selected_source_paths: List of selected file paths
        """
        await self._db.execute("""
            INSERT OR REPLACE INTO chat_sessions
            (session_id, selected_source_paths, last_accessed)
            VALUES (?, ?, ?)
        """, (session_id, json.dumps(selected_source_paths), datetime.now()))
        await self._db.commit()
        logger.debug(f"Saved session {session_id} with {len(selected_source_paths)} sources")

    async def get_sources(self, session_id: str) -> list[str]:
        """Get selected sources for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of selected file paths, empty list if session not found
        """
        cursor = await self._db.execute(
            "SELECT selected_source_paths FROM chat_sessions WHERE session_id = ?",
            (session_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return []
        return json.loads(row["selected_source_paths"])

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get full session data.

        Args:
            session_id: Session identifier

        Returns:
            Session dict with sources and metadata, None if not found
        """
        cursor = await self._db.execute(
            """
            SELECT session_id, selected_source_paths, created_at, last_accessed
            FROM chat_sessions
            WHERE session_id = ?
            """,
            (session_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return {
            "session_id": row["session_id"],
            "selected_source_paths": json.loads(row["selected_source_paths"]),
            "created_at": row["created_at"],
            "last_accessed": row["last_accessed"],
        }

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and its conversation history.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        cursor = await self._db.execute(
            "DELETE FROM chat_sessions WHERE session_id = ?",
            (session_id,),
        )
        await self._db.execute(
            "DELETE FROM conversation_history WHERE session_id = ?",
            (session_id,),
        )
        await self._db.commit()
        return cursor.rowcount > 0

    async def save_message(
        self,
        session_id: str,
        message_index: int,
        role: str,
        content: str,
    ) -> None:
        """Save a conversation message.

        Args:
            session_id: Session identifier
            message_index: Message index in conversation (0-based)
            role: 'user' or 'assistant'
            content: Message content
        """
        await self._db.execute(
            """
            INSERT OR REPLACE INTO conversation_history
            (session_id, message_index, role, content)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, message_index, role, content),
        )
        await self._db.commit()

    async def get_conversation_history(
        self,
        session_id: str,
    ) -> list[dict]:
        """Get conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of message dicts with role, content, index
        """
        cursor = await self._db.execute(
            """
            SELECT message_index, role, content, created_at
            FROM conversation_history
            WHERE session_id = ?
            ORDER BY message_index ASC
            """,
            (session_id,),
        )
        rows = await cursor.fetchall()
        return [
            {
                "message_index": row["message_index"],
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    async def clear_conversation(self, session_id: str) -> None:
        """Clear conversation history for a session.

        Args:
            session_id: Session identifier
        """
        await self._db.execute(
            "DELETE FROM conversation_history WHERE session_id = ?",
            (session_id,),
        )
        await self._db.commit()

    async def list_sessions(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """List all sessions with pagination.

        Args:
            limit: Maximum number of sessions to return
            offset: Offset for pagination

        Returns:
            List of session dicts
        """
        cursor = await self._db.execute(
            """
            SELECT session_id, created_at, last_accessed
            FROM chat_sessions
            ORDER BY last_accessed DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [
            {
                "session_id": row["session_id"],
                "created_at": row["created_at"],
                "last_accessed": row["last_accessed"],
            }
            for row in rows
        ]

    async def cleanup_expired(self, days: int = 30) -> int:
        """Clean up expired sessions.

        Args:
            days: Sessions not accessed for this many days are expired

        Returns:
            Number of sessions deleted
        """
        cutoff = datetime.now() - timedelta(days=days)
        cursor = await self._db.execute(
            "DELETE FROM chat_sessions WHERE last_accessed < ?",
            (cutoff,),
        )
        await self._db.commit()
        deleted = cursor.rowcount
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired sessions")
        return deleted

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None
            logger.info("Closed chat session database")


__all__ = ["ChatSessionDB"]
