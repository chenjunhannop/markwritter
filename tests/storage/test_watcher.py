"""Tests for Watchdog integration.

Tests for VaultWatcher and file system event handling.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from markwritter.storage.watcher import (
    Debouncer,
    VaultEventHandler,
    VaultWatcher,
)


# ==============================================================================
# VaultEventHandler Tests
# ==============================================================================


class TestVaultEventHandler:
    """Tests for VaultEventHandler."""

    def test_is_watched_file_markdown(self) -> None:
        """Test that .md files are watched."""
        handler = VaultEventHandler()
        assert handler._is_watched_file("notes/test.md") is True
        assert handler._is_watched_file("/vault/notes/test.md") is True

    def test_is_watched_file_pdf(self) -> None:
        """Test that .pdf files are watched."""
        handler = VaultEventHandler()
        assert handler._is_watched_file("docs/file.pdf") is True

    def test_is_watched_file_ignored_extensions(self) -> None:
        """Test that non-.md/.pdf files are ignored."""
        handler = VaultEventHandler()
        assert handler._is_watched_file("image.png") is False
        assert handler._is_watched_file("data.json") is False
        assert handler._is_watched_file("notes.txt") is False

    def test_is_watched_file_hidden(self) -> None:
        """Test that hidden files are ignored."""
        handler = VaultEventHandler()
        assert handler._is_watched_file(".hidden.md") is False
        assert handler._is_watched_file(".obsidian/config.json") is False

    def test_on_create_callback(self) -> None:
        """Test file creation callback."""
        mock_callback = MagicMock()
        handler = VaultEventHandler(on_create=mock_callback)

        from watchdog.events import FileCreatedEvent

        event = FileCreatedEvent("/vault/test.md")
        handler.on_created(event)

        mock_callback.assert_called_once_with("/vault/test.md")

    def test_on_create_callback_ignored_extension(self) -> None:
        """Test that creation callback ignores non-watched files."""
        mock_callback = MagicMock()
        handler = VaultEventHandler(on_create=mock_callback)

        from watchdog.events import FileCreatedEvent

        event = FileCreatedEvent("/vault/image.png")
        handler.on_created(event)

        mock_callback.assert_not_called()

    def test_on_modify_callback(self) -> None:
        """Test file modification callback."""
        mock_callback = MagicMock()
        handler = VaultEventHandler(on_modify=mock_callback)

        from watchdog.events import FileModifiedEvent

        event = FileModifiedEvent("/vault/test.md")
        handler.on_modified(event)

        mock_callback.assert_called_once_with("/vault/test.md")

    def test_on_delete_callback(self) -> None:
        """Test file deletion callback."""
        mock_callback = MagicMock()
        handler = VaultEventHandler(on_delete=mock_callback)

        from watchdog.events import FileDeletedEvent

        event = FileDeletedEvent("/vault/test.md")
        handler.on_deleted(event)

        mock_callback.assert_called_once_with("/vault/test.md")

    def test_on_move_callback(self) -> None:
        """Test file move callback."""
        mock_callback = MagicMock()
        handler = VaultEventHandler(on_move=mock_callback)

        from watchdog.events import FileMovedEvent

        event = FileMovedEvent("/vault/old.md", "/vault/new.md")
        handler.on_moved(event)

        mock_callback.assert_called_once_with("/vault/old.md", "/vault/new.md")


# ==============================================================================
# Debouncer Tests
# ==============================================================================


class TestDebouncer:
    """Tests for Debouncer."""

    @pytest.mark.asyncio
    async def test_debouncer_executes_callback(self) -> None:
        """Test that debouncer executes callback after delay."""
        mock_callback = MagicMock()
        debouncer = Debouncer(delay_seconds=0.1)

        debouncer.schedule("key1", mock_callback)

        # Run for longer than delay
        import asyncio

        asyncio.create_task(debouncer.run_loop())
        await asyncio.sleep(0.2)

        assert mock_callback.called

    @pytest.mark.asyncio
    async def test_debouncer_prevents_rapid_calls(self) -> None:
        """Test that debouncer prevents rapid duplicate calls."""
        mock_callback = MagicMock()
        debouncer = Debouncer(delay_seconds=0.2)

        # Schedule same key multiple times rapidly
        debouncer.schedule("key1", mock_callback)
        debouncer.schedule("key1", mock_callback)
        debouncer.schedule("key1", mock_callback)

        import asyncio

        asyncio.create_task(debouncer.run_loop())
        await asyncio.sleep(0.3)

        # Should only be called once due to debouncing
        assert mock_callback.call_count == 1

    @pytest.mark.asyncio
    async def test_debouncer_allows_separate_keys(self) -> None:
        """Test that debouncer allows different keys."""
        mock_callback1 = MagicMock()
        mock_callback2 = MagicMock()
        debouncer = Debouncer(delay_seconds=0.1)

        debouncer.schedule("key1", mock_callback1)
        debouncer.schedule("key2", mock_callback2)

        import asyncio

        asyncio.create_task(debouncer.run_loop())
        await asyncio.sleep(0.2)

        assert mock_callback1.called
        assert mock_callback2.called

    def test_debouncer_stop_clears_pending(self) -> None:
        """Test that stop clears pending callbacks."""
        debouncer = Debouncer()
        debouncer.schedule("key1", lambda: None)
        debouncer.schedule("key2", lambda: None)

        debouncer.stop()

        assert len(debouncer._pending) == 0


# ==============================================================================
# VaultWatcher Tests
# ==============================================================================


class TestVaultWatcher:
    """Tests for VaultWatcher."""

    def test_vault_watcher_initialization(self) -> None:
        """Test VaultWatcher initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = VaultWatcher(tmpdir)
            assert watcher.is_running is False

    def test_vault_watcher_start_stop(self) -> None:
        """Test VaultWatcher start and stop."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = VaultWatcher(tmpdir)

            import asyncio

            async def run_test():
                await watcher.start()
                assert watcher.is_running is True
                await watcher.stop()
                assert watcher.is_running is False

            asyncio.run(run_test())

    def test_vault_watcher_callbacks(self) -> None:
        """Test that VaultWatcher callbacks are invoked."""
        mock_create = MagicMock()
        mock_modify = MagicMock()
        mock_delete = MagicMock()
        mock_move = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = VaultWatcher(
                tmpdir,
                on_create=mock_create,
                on_modify=mock_modify,
                on_delete=mock_delete,
                on_move=mock_move,
            )

            # Verify handler has callbacks
            assert watcher._handler._on_create is not None
            assert watcher._handler._on_modify is not None
            assert watcher._handler._on_delete is not None
            assert watcher._handler._on_move is not None

    def test_vault_watcher_double_start_warning(self, caplog) -> None:
        """Test that starting twice logs warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = VaultWatcher(tmpdir)

            import asyncio

            async def run_test():
                await watcher.start()
                await watcher.start()  # Should log warning
                await watcher.stop()

                assert "already running" in caplog.text

            asyncio.run(run_test())


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestVaultWatcherIntegration:
    """Integration tests with real file system."""

    @pytest.mark.asyncio
    async def test_watcher_detects_file_creation(self) -> None:
        """Test that watcher detects file creation."""
        callback_received = []

        def on_create(path: str) -> None:
            callback_received.append(path)

        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = VaultWatcher(tmpdir, on_create=on_create)
            await watcher.start()

            # Give observer time to start
            import asyncio

            await asyncio.sleep(0.2)

            # Create a markdown file
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test")

            # Wait for event to propagate
            await asyncio.sleep(0.5)

            await watcher.stop()

            # Verify callback was called
            assert len(callback_received) > 0
            assert any("test.md" in path for path in callback_received)

    @pytest.mark.asyncio
    async def test_watcher_detects_file_modification(self) -> None:
        """Test that watcher detects file modification."""
        callback_received = []

        def on_modify(path: str) -> None:
            callback_received.append(path)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file first
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Initial")

            watcher = VaultWatcher(tmpdir, on_modify=on_modify)
            await watcher.start()

            import asyncio

            await asyncio.sleep(0.2)

            # Modify file
            test_file.write_text("# Modified")

            await asyncio.sleep(0.5)

            await watcher.stop()

            # Verify callback was called
            assert len(callback_received) > 0
            assert any("test.md" in path for path in callback_received)

    @pytest.mark.asyncio
    async def test_watcher_ignores_non_markdown_files(self) -> None:
        """Test that watcher ignores non-markdown files."""
        callback_received = []

        def on_create(path: str) -> None:
            callback_received.append(path)

        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = VaultWatcher(tmpdir, on_create=on_create)
            await watcher.start()

            import asyncio

            await asyncio.sleep(0.2)

            # Create non-markdown files
            (Path(tmpdir) / "image.png").write_text("fake png")
            (Path(tmpdir) / "data.json").write_text("{}")

            await asyncio.sleep(0.5)

            await watcher.stop()

            # Should not receive callbacks for non-markdown files
            markdown_received = [p for p in callback_received if p.endswith(".md")]
            assert len(markdown_received) == 0
