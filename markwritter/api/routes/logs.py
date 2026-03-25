"""Logs API router with SSE streaming."""

import asyncio
import queue

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/logs", tags=["logs"])

# Global log queue for cross-thread communication
log_queue: queue.Queue = queue.Queue()


def add_log_entry(entry: str) -> None:
    """Add a log entry to the stream queue."""
    log_queue.put(entry)


@router.get("/stream")
async def stream_logs():
    """Stream logs via SSE."""

    async def log_generator():
        while True:
            try:
                # Non-blocking get with timeout
                log_entry = log_queue.get(timeout=1.0)
                yield f"data: {log_entry}\n\n"
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield ": heartbeat\n\n"
            except asyncio.CancelledError:
                break

    return StreamingResponse(
        log_generator(),
        media_type="text/event-stream",
    )
