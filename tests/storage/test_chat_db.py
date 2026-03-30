"""Tests for ChatSessionDB."""

import tempfile
from pathlib import Path

import pytest

from markwritter.storage.chat_db import ChatSessionDB


@pytest.fixture
async def chat_db() -> "ChatSessionDB":
    """Create a temporary chat session database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "chat_sessions.db"
        db = ChatSessionDB(db_path)
        await db.initialize()
        yield db
        await db.close()


class TestChatSessionDB:
    """Tests for ChatSessionDB."""

    @pytest.mark.asyncio
    async def test_save_and_get_session(self, chat_db: ChatSessionDB) -> None:
        """Test saving and retrieving a session."""
        session_id = "test-session-123"
        sources = ["notes/a.md", "notes/b.md"]

        await chat_db.save_session(session_id, sources)
        result = await chat_db.get_sources(session_id)

        assert result == sources

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, chat_db: ChatSessionDB) -> None:
        """Test getting nonexistent session returns empty list."""
        result = await chat_db.get_sources("nonexistent")
        assert result == []

    @pytest.mark.asyncio
    async def test_update_session(self, chat_db: ChatSessionDB) -> None:
        """Test updating session sources."""
        session_id = "test-session"

        await chat_db.save_session(session_id, ["a.md"])
        await chat_db.save_session(session_id, ["b.md", "c.md"])

        result = await chat_db.get_sources(session_id)
        assert result == ["b.md", "c.md"]

    @pytest.mark.asyncio
    async def test_delete_session(self, chat_db: ChatSessionDB) -> None:
        """Test deleting a session."""
        session_id = "test-session"
        await chat_db.save_session(session_id, ["a.md"])

        result = await chat_db.delete_session(session_id)
        assert result is True

        # Verify deleted
        sources = await chat_db.get_sources(session_id)
        assert sources == []

    @pytest.mark.asyncio
    async def test_delete_nonexistent_session(self, chat_db: ChatSessionDB) -> None:
        """Test deleting nonexistent session returns False."""
        result = await chat_db.delete_session("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_save_and_get_message(self, chat_db: ChatSessionDB) -> None:
        """Test saving and retrieving conversation messages."""
        session_id = "test-session"

        await chat_db.save_message(session_id, 0, "user", "Hello")
        await chat_db.save_message(session_id, 1, "assistant", "Hi there!")

        history = await chat_db.get_conversation_history(session_id)

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"

    @pytest.mark.asyncio
    async def test_update_message(self, chat_db: ChatSessionDB) -> None:
        """Test updating existing message."""
        session_id = "test-session"

        await chat_db.save_message(session_id, 0, "user", "Original")
        await chat_db.save_message(session_id, 0, "user", "Updated")

        history = await chat_db.get_conversation_history(session_id)

        assert len(history) == 1
        assert history[0]["content"] == "Updated"

    @pytest.mark.asyncio
    async def test_clear_conversation(self, chat_db: ChatSessionDB) -> None:
        """Test clearing conversation history."""
        session_id = "test-session"

        await chat_db.save_message(session_id, 0, "user", "Hello")
        await chat_db.save_message(session_id, 1, "assistant", "Hi")

        await chat_db.clear_conversation(session_id)

        history = await chat_db.get_conversation_history(session_id)
        assert len(history) == 0

    @pytest.mark.asyncio
    async def test_get_full_session(self, chat_db: ChatSessionDB) -> None:
        """Test getting full session data."""
        session_id = "test-session"
        sources = ["a.md", "b.md"]

        await chat_db.save_session(session_id, sources)
        session = await chat_db.get_session(session_id)

        assert session is not None
        assert session["session_id"] == session_id
        assert session["selected_source_paths"] == sources
        assert "created_at" in session
        assert "last_accessed" in session

    @pytest.mark.asyncio
    async def test_get_nonexistent_full_session(self, chat_db: ChatSessionDB) -> None:
        """Test getting nonexistent full session returns None."""
        session = await chat_db.get_session("nonexistent")
        assert session is None

    @pytest.mark.asyncio
    async def test_list_sessions(self, chat_db: ChatSessionDB) -> None:
        """Test listing sessions with pagination."""
        # Create multiple sessions
        for i in range(5):
            await chat_db.save_session(f"session-{i}", [f"file{i}.md"])

        # List all
        sessions = await chat_db.list_sessions(limit=10, offset=0)
        assert len(sessions) == 5

        # List with pagination
        sessions = await chat_db.list_sessions(limit=2, offset=0)
        assert len(sessions) == 2

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, chat_db: ChatSessionDB) -> None:
        """Test cleaning up expired sessions."""
        # Create a session
        await chat_db.save_session("active-session", ["a.md"])

        # Manually update last_accessed to be old
        await chat_db._db.execute(
            """
            UPDATE chat_sessions
            SET last_accessed = datetime('now', '-60 days')
            WHERE session_id = 'active-session'
            """
        )
        await chat_db._db.commit()

        # Cleanup sessions older than 30 days
        deleted = await chat_db.cleanup_expired(days=30)
        assert deleted == 1

        # Verify session was deleted
        sources = await chat_db.get_sources("active-session")
        assert sources == []

    @pytest.mark.asyncio
    async def test_conversation_order(self, chat_db: ChatSessionDB) -> None:
        """Test conversation history is ordered correctly."""
        session_id = "test-session"

        # Save messages out of order
        await chat_db.save_message(session_id, 2, "user", "Third")
        await chat_db.save_message(session_id, 0, "user", "First")
        await chat_db.save_message(session_id, 1, "assistant", "Second")

        history = await chat_db.get_conversation_history(session_id)

        assert len(history) == 3
        assert history[0]["content"] == "First"
        assert history[1]["content"] == "Second"
        assert history[2]["content"] == "Third"
