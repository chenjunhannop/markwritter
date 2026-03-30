"""Watchdog-based file system event listener for incremental indexing.

This module provides VaultWatcher, which uses the watchdog library to listen
for file system events in the Obsidian vault and trigger incremental reindexing.

Features:
- Real-time file change detection (create, modify, delete, rename)
- Debouncing to avoid rapid re-indexing
- Selective filtering (.md and .pdf files only)
- Cross-platform support (macOS FSEvents, Linux inotify, Windows ReadDirectoryChangesW)

Performance:
- Eliminates polling overhead (CPU/IO savings)
- Responds to changes within ~100ms vs polling interval (e.g., 30s)
"""

import asyncio
import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import Optional

from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class VaultEventHandler(FileSystemEventHandler):
    """Handle file system events for Obsidian vault.

    Filters and dispatches events for markdown and PDF files only.
    """

    def __init__(
        self,
        on_create: Optional[Callable[[str], None]] = None,
        on_modify: Optional[Callable[[str], None]] = None,
        on_delete: Optional[Callable[[str], None]] = None,
        on_move: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        """Initialize event handler.

        Args:
            on_create: Callback for new files
            on_modify: Callback for modified files
            on_delete: Callback for deleted files
            on_move: Callback for moved/renamed files (old_path, new_path)
        """
        super().__init__()
        self._on_create = on_create
        self._on_modify = on_modify
        self._on_delete = on_delete
        self._on_move = on_move

    def _is_watched_file(self, path: str) -> bool:
        """Check if file should be watched.

        Args:
            path: File path to check

        Returns:
            True if file is .md or .pdf and not hidden
        """
        path_obj = Path(path)
        # Check extension
        if path_obj.suffix.lower() not in (".md", ".pdf"):
            return False
        # Check not hidden
        if path_obj.name.startswith("."):
            return False
        return True

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation event."""
        if isinstance(event, FileCreatedEvent) and self._is_watched_file(event.src_path):
            logger.info(f"File created: {event.src_path}")
            if self._on_create:
                self._on_create(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification event."""
        if isinstance(event, FileModifiedEvent) and self._is_watched_file(event.src_path):
            logger.debug(f"File modified: {event.src_path}")
            if self._on_modify:
                self._on_modify(event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion event."""
        if isinstance(event, FileDeletedEvent) and self._is_watched_file(event.src_path):
            logger.info(f"File deleted: {event.src_path}")
            if self._on_delete:
                self._on_delete(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move/rename event."""
        if isinstance(event, FileMovedEvent):
            if self._is_watched_file(event.src_path) or self._is_watched_file(
                event.dest_path
            ):
                logger.info(f"File moved: {event.src_path} → {event.dest_path}")
                if self._on_move:
                    self._on_move(event.src_path, event.dest_path)


class Debouncer:
    """Debounce rapid file system events.

    Prevents multiple rapid triggers (e.g., save operations that
    write multiple times) from causing redundant reindexing.
    """

    def __init__(self, delay_seconds: float = 0.5) -> None:
        """Initialize debouncer.

        Args:
            delay_seconds: Minimum time between triggers
        """
        self._delay = delay_seconds
        self._last_triggered: dict[str, float] = {}
        self._pending: dict[str, Callable] = {}

    def schedule(self, key: str, callback: Callable) -> None:
        """Schedule a callback with debouncing.

        Args:
            key: Unique key for debouncing (e.g., file path)
            callback: Function to call after debounce delay
        """
        self._pending[key] = callback

    async def run_loop(self) -> None:
        """Run the debouncer event loop.

        Continuously checks for pending callbacks and executes them
        after the debounce delay has passed.
        """
        while True:
            now = time.time()
            to_execute = []

            for key, callback in list(self._pending.items()):
                last_time = self._last_triggered.get(key, 0)
                if now - last_time >= self._delay:
                    to_execute.append((key, callback))

            for key, callback in to_execute:
                try:
                    callback()
                    self._last_triggered[key] = now
                except Exception as e:
                    logger.error(f"Error executing callback for {key}: {e}")
                finally:
                    del self._pending[key]

            await asyncio.sleep(0.1)  # Check every 100ms

    def stop(self) -> None:
        """Stop the debouncer and clear pending callbacks."""
        self._pending.clear()


class VaultWatcher:
    """Watch Obsidian vault for file system changes.

    Uses watchdog to listen for file events and triggers callbacks
    for incremental indexing.

    Example:
        >>> async def on_modify(path):
        ...     await reindex_file(path)
        >>>
        >>> watcher = VaultWatcher(vault_path, on_modify=on_modify)
        >>> await watcher.start()
        >>> # ... running ...
        >>> await watcher.stop()
    """

    def __init__(
        self,
        vault_path: Path | str,
        on_create: Optional[Callable[[str], None]] = None,
        on_modify: Optional[Callable[[str], None]] = None,
        on_delete: Optional[Callable[[str], None]] = None,
        on_move: Optional[Callable[[str, str], None]] = None,
        debounce_seconds: float = 0.5,
    ) -> None:
        """Initialize vault watcher.

        Args:
            vault_path: Path to Obsidian vault
            on_create: Callback for new files
            on_modify: Callback for modified files
            on_delete: Callback for deleted files
            on_move: Callback for moved/renamed files
            debounce_seconds: Debounce delay for events
        """
        self._vault_path = Path(vault_path)
        self._observer: Optional[Observer] = None
        self._debouncer = Debouncer(delay_seconds=debounce_seconds)
        self._running = False

        # Wrap callbacks to work with debouncer
        self._create_callback = on_create
        self._modify_callback = on_modify
        self._delete_callback = on_delete
        self._move_callback = on_move

        self._handler = VaultEventHandler(
            on_create=self._on_create,
            on_modify=self._on_modify,
            on_delete=self._on_delete,
            on_move=self._on_move,
        )

    def _on_create(self, path: str) -> None:
        """Handle create event with debouncing."""
        if self._create_callback:
            self._debouncer.schedule(path, lambda: self._create_callback(path))

    def _on_modify(self, path: str) -> None:
        """Handle modify event with debouncing."""
        if self._modify_callback:
            self._debouncer.schedule(path, lambda: self._modify_callback(path))

    def _on_delete(self, path: str) -> None:
        """Handle delete event with debouncing."""
        if self._delete_callback:
            self._debouncer.schedule(path, lambda: self._delete_callback(path))

    def _on_move(self, old_path: str, new_path: str) -> None:
        """Handle move event with debouncing."""
        if self._move_callback:
            self._debouncer.schedule(
                f"{old_path}:{new_path}",
                lambda: self._move_callback(old_path, new_path),
            )

    async def start(self) -> None:
        """Start watching the vault.

        Runs the observer and debouncer in background tasks.
        """
        if self._running:
            logger.warning("VaultWatcher is already running")
            return

        self._running = True

        # Start filesystem observer
        self._observer = Observer()
        self._observer.schedule(
            self._handler,
            str(self._vault_path),
            recursive=True,
        )
        self._observer.start()
        logger.info(f"Started watching vault: {self._vault_path}")

        # Start debouncer loop
        asyncio.create_task(self._debouncer.run_loop())

    async def stop(self) -> None:
        """Stop watching the vault."""
        if not self._running:
            return

        self._running = False

        # Stop debouncer
        self._debouncer.stop()

        # Stop observer
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("Stopped watching vault")

    @property
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running


__all__ = ["VaultWatcher", "VaultEventHandler", "Debouncer"]
