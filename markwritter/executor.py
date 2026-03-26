"""Subagent executor for running skills."""

import asyncio
import logging
import warnings
from pathlib import Path

from markwritter.models import ExecutionResult, SkillDefinition

logger = logging.getLogger(__name__)


class SkillExecutor:
    """Executor that runs skills as subagents."""

    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir

    async def execute(
        self,
        skill: SkillDefinition,
        params: dict[str, str],
    ) -> ExecutionResult:
        """Execute a skill with given parameters."""
        skill_dir = self.skills_dir / skill.name
        script_path = skill_dir / skill.execution.script

        if not script_path.exists():
            return ExecutionResult(
                success=False,
                error=f"Script not found: {script_path}",
                exit_code=1,
            )

        # Build command
        cmd = [skill.execution.command, str(script_path)]

        # Add parameters as arguments
        for input_def in skill.inputs:
            value = params.get(input_def.name)
            if value is None:
                if input_def.required and input_def.default is None:
                    return ExecutionResult(
                        success=False,
                        error=f"Missing required parameter: {input_def.name}",
                        exit_code=1,
                    )
                value = input_def.default

            if value is not None:
                cmd.extend([f"--{input_def.name}", str(value)])

        # Execute subprocess
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=(
                    skill_dir
                    if skill.execution.working_dir is None
                    else skill.execution.working_dir
                ),
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=skill.execution.timeout,
            )

            return ExecutionResult(
                success=process.returncode == 0,
                output=stdout.decode("utf-8", errors="replace").strip(),
                error=stderr.decode("utf-8", errors="replace").strip(),
                exit_code=process.returncode or 0,
            )

        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                error=f"Skill execution timed out after {skill.execution.timeout}s",
                exit_code=-1,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Execution failed: {e}",
                exit_code=-1,
            )

    def execute_sync(
        self,
        skill: SkillDefinition,
        params: dict[str, str],
    ) -> ExecutionResult:
        """Synchronous wrapper for execute.

        WARNING: This method uses asyncio.run() which should not be called
        from within an async context. Use execute() instead in async code.

        This method will raise a RuntimeError if called from within an
        async context (e.g., inside a FastAPI route handler).

        Args:
            skill: Skill definition to execute
            params: Parameters for the skill

        Returns:
            ExecutionResult from the skill execution

        Raises:
            RuntimeError: If called from within an async context
        """
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            # If we get here, we're in an async context
            raise RuntimeError(
                "execute_sync() cannot be called from within an async context. "
                "Use execute() instead."
            )
        except RuntimeError as e:
            if "no running event loop" in str(e):
                # This is expected - we're not in an async context
                pass
            else:
                # Re-raise the RuntimeError we just created
                raise

        # Issue deprecation warning
        warnings.warn(
            "execute_sync() is deprecated. Use execute() with asyncio.run() "
            "or async/await pattern instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        logger.warning(
            "execute_sync() called - consider using async execute() instead"
        )
        return asyncio.run(self.execute(skill, params))
