"""Agent workflow orchestration.

AgentFlow orchestrates the execution of agent tasks:
- Task parsing and routing
- Model/skill selection
- Tool invocation
- Subagent spawning
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from markwritter.agent.scope import AgentScope
from markwritter.agent.subagent import SubagentRegistry
from markwritter.agent.provider import ProviderRegistry

logger = logging.getLogger(__name__)


class AgentFlow:
    """Agent workflow orchestrator.

    AgentFlow manages the execution flow of an agent:
    1. Parse the incoming task
    2. Select appropriate model and skills
    3. Execute the task with available tools
    4. Optionally spawn subagents for subtasks

    Attributes:
        scope: Agent execution context
        provider_registry: LLM provider registry
        subagent_registry: Optional subagent management

    Example:
        >>> scope = AgentScope(name="researcher", model="gpt-4")
        >>> registry = ProviderRegistry()
        >>> flow = AgentFlow(scope, registry)
        >>> result = await flow.run("Search for Python tutorials")
    """

    def __init__(
        self,
        scope: AgentScope,
        provider_registry: ProviderRegistry,
        subagent_registry: Optional[SubagentRegistry] = None,
    ) -> None:
        """Initialize AgentFlow.

        Args:
            scope: Agent execution context
            provider_registry: LLM provider registry
            subagent_registry: Optional subagent registry (created if not provided)
        """
        self._scope = scope
        self._provider_registry = provider_registry
        self._subagent_registry = subagent_registry or SubagentRegistry()

    @property
    def scope(self) -> AgentScope:
        """Return the agent scope."""
        return self._scope

    @property
    def provider_registry(self) -> ProviderRegistry:
        """Return the provider registry."""
        return self._provider_registry

    @property
    def subagent_registry(self) -> Optional[SubagentRegistry]:
        """Return the subagent registry."""
        return self._subagent_registry

    async def run(
        self,
        task: str,
        *,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Execute a task.

        Args:
            task: Task description
            on_progress: Optional callback for progress updates

        Returns:
            Task result string

        Raises:
            ValueError: If task is empty
            Exception: If execution fails
        """
        # Validate task
        task = task.strip()
        if not task:
            raise ValueError("Task cannot be empty")

        logger.info(f"Agent '{self._scope.name}' starting task: {task[:50]}...")

        if on_progress:
            on_progress(f"Starting task: {task}")

        # Parse task and determine execution plan
        execution_plan = self._parse_task(task)

        if on_progress:
            on_progress(f"Execution plan: {execution_plan}")

        # Execute with selected model/skill
        result = await self._execute_plan(execution_plan, task, on_progress)

        logger.info(f"Agent '{self._scope.name}' completed task")

        return result

    def spawn_subagent(self, name: str, task: str) -> str:
        """Spawn a subagent for a subtask.

        Args:
            name: Name of the subagent (must be in scope.subagents)
            task: Task for the subagent

        Returns:
            Subagent run ID

        Raises:
            ValueError: If subagent name is not found or no registry
        """
        if not self._subagent_registry:
            raise ValueError("No subagent registry configured")

        # Get the model for this subagent
        model = self._scope.get_subagent_model(name)
        if not model:
            raise ValueError(f"Unknown subagent: {name}")

        logger.info(f"Spawning subagent '{name}' with model '{model}'")

        run_id = self._subagent_registry.spawn(name, model, task)

        return run_id

    def get_context(self) -> dict[str, Any]:
        """Get the execution context.

        Returns:
            Dictionary with agent context information
        """
        return {
            "name": self._scope.name,
            "model": self._scope.model,
            "workspace": self._scope.workspace,
            "skills": list(self._scope.skills),
            "tools": list(self._scope.tools),
            "memory_search": self._scope.memory_search,
            "subagents": dict(self._scope.subagents),
        }

    def _parse_task(self, task: str) -> dict[str, Any]:
        """Parse task and determine execution plan.

        Args:
            task: Task description

        Returns:
            Execution plan dictionary
        """
        plan: dict[str, Any] = {
            "task": task,
            "model": self._scope.model,
            "skills": [],
            "tools": [],
        }

        # Check for skill keywords in task
        task_lower = task.lower()

        for skill in self._scope.skills:
            skill_keyword = skill.replace("_", " ")
            if skill_keyword in task_lower or skill in task_lower:
                plan["skills"].append(skill)

        # Determine which tools might be needed
        tool_keywords = {
            "web_search": ["search", "find", "look up", "web"],
            "code_exec": ["execute", "run", "code", "script"],
        }

        for tool in self._scope.tools:
            keywords = tool_keywords.get(tool, [])
            if any(kw in task_lower for kw in keywords):
                plan["tools"].append(tool)

        return plan

    async def _execute_plan(
        self,
        plan: dict[str, Any],
        task: str,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Execute the execution plan.

        Args:
            plan: Execution plan from _parse_task
            task: Original task
            on_progress: Optional progress callback

        Returns:
            Execution result
        """
        model = plan["model"]
        skills = plan["skills"]
        tools = plan["tools"]

        # Build prompt with context
        prompt = self._build_prompt(task, skills, tools)

        if on_progress:
            on_progress(f"Executing with model: {model}")

        # Call LLM
        try:
            result = self._provider_registry.complete(
                prompt,
                model=model,
            )
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            raise

        return result

    def _build_prompt(
        self,
        task: str,
        skills: list[str],
        tools: list[str],
    ) -> str:
        """Build the prompt for LLM.

        Args:
            task: Task description
            skills: Available skills
            tools: Available tools

        Returns:
            Formatted prompt string
        """
        parts = [f"You are agent '{self._scope.name}'."]

        if skills:
            parts.append(f"Available skills: {', '.join(skills)}")

        if tools:
            parts.append(f"Available tools: {', '.join(tools)}")

        parts.append(f"\nTask: {task}")
        parts.append("\nResponse:")

        return "\n".join(parts)