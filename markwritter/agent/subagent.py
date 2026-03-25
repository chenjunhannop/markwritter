"""Subagent registry for managing subagent runs.

SubagentRegistry provides:
- Spawning subagent runs
- Tracking run status
- Executing skills within runs
- Announcing progress messages
- Cleanup of completed runs
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SubagentStatus(Enum):
    """Status of a subagent run."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SubagentRun:
    """Record of a subagent run.

    Attributes:
        id: Unique identifier for this run
        name: Name of the subagent
        model: LLM model used by the subagent
        task: Task description
        status: Current status of the run
        result: Result of the run (if completed)
        error: Error message (if failed)
    """

    id: str
    name: str
    model: str
    task: str
    status: SubagentStatus
    result: Optional[str] = None
    error: Optional[str] = None


class SubagentRegistry:
    """Registry for managing subagent runs.

    The SubagentRegistry handles the lifecycle of subagent runs:
    - spawn: Create a new run with IDLE status
    - execute: Execute a skill within the run
    - announce: Send progress messages
    - cleanup: Remove completed runs

    Example:
        >>> registry = SubagentRegistry()
        >>> run_id = registry.spawn("researcher", "gpt-4", "Search for info")
        >>> result = registry.execute(run_id, "web_search", {"query": "test"})
        >>> registry.cleanup(run_id)
    """

    def __init__(self) -> None:
        """Initialize the registry."""
        self._runs: dict[str, SubagentRun] = {}

    def spawn(self, name: str, model: str, task: str) -> str:
        """Spawn a new subagent run.

        Args:
            name: Name of the subagent
            model: LLM model to use
            task: Task description

        Returns:
            Unique run ID

        Example:
            >>> registry = SubagentRegistry()
            >>> run_id = registry.spawn("researcher", "gpt-4", "Search for info")
        """
        run_id = str(uuid.uuid4())

        run = SubagentRun(
            id=run_id,
            name=name,
            model=model,
            task=task,
            status=SubagentStatus.IDLE,
        )

        self._runs[run_id] = run
        return run_id

    def execute(self, run_id: str, skill: str, params: dict[str, Any]) -> str:
        """Execute a skill within a subagent run.

        Args:
            run_id: Run ID from spawn()
            skill: Name of the skill to execute
            params: Parameters for the skill

        Returns:
            Result string from the skill execution

        Raises:
            ValueError: If run_id is not found

        Example:
            >>> registry = SubagentRegistry()
            >>> run_id = registry.spawn("agent", "gpt-4", "task")
            >>> result = registry.execute(run_id, "skill", {"param": "value"})
        """
        run = self._runs.get(run_id)
        if run is None:
            raise ValueError(f"Run '{run_id}' not found")

        # Update status to running
        run.status = SubagentStatus.RUNNING

        try:
            # In a real implementation, this would execute the skill
            # For now, return a placeholder result
            result = f"Executed skill '{skill}' with params: {params}"

            run.status = SubagentStatus.COMPLETED
            run.result = result

            return result

        except Exception as e:
            run.status = SubagentStatus.FAILED
            run.error = str(e)
            raise

    def get_status(self, run_id: str) -> Optional[SubagentStatus]:
        """Get the status of a subagent run.

        Args:
            run_id: Run ID from spawn()

        Returns:
            SubagentStatus or None if not found
        """
        run = self._runs.get(run_id)
        return run.status if run else None

    def get_run(self, run_id: str) -> Optional[SubagentRun]:
        """Get the run record.

        Args:
            run_id: Run ID from spawn()

        Returns:
            SubagentRun or None if not found
        """
        return self._runs.get(run_id)

    def announce(self, run_id: str, message: str) -> None:
        """Announce a progress message for a run.

        Args:
            run_id: Run ID from spawn()
            message: Progress message

        Raises:
            ValueError: If run_id is not found

        Example:
            >>> registry = SubagentRegistry()
            >>> run_id = registry.spawn("agent", "gpt-4", "task")
            >>> registry.announce(run_id, "Progress: 50%")
        """
        run = self._runs.get(run_id)
        if run is None:
            raise ValueError(f"Run '{run_id}' not found")

        # In a real implementation, this would publish the message
        # to subscribers or log it
        # For now, just store it as an annotation
        pass

    def cleanup(self, run_id: str) -> None:
        """Remove a run from the registry.

        Args:
            run_id: Run ID from spawn()

        Example:
            >>> registry = SubagentRegistry()
            >>> run_id = registry.spawn("agent", "gpt-4", "task")
            >>> registry.cleanup(run_id)
        """
        self._runs.pop(run_id, None)

    def list_runs(self, status: Optional[SubagentStatus] = None) -> list[SubagentRun]:
        """List all runs, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of SubagentRun records
        """
        if status is None:
            return list(self._runs.values())

        return [run for run in self._runs.values() if run.status == status]