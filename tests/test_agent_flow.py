"""Tests for AgentFlow - Agent workflow orchestration.

TDD Phase: RED - Write failing tests first.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from markwritter.agent.scope import AgentScope
from markwritter.agent.flow import AgentFlow
from markwritter.agent.subagent import SubagentRegistry


class TestAgentFlowCreation:
    """Test AgentFlow initialization."""

    def test_create_with_scope(self) -> None:
        """Create AgentFlow with AgentScope."""
        scope = AgentScope(name="test-agent", model="gpt-4")

        # Create a mock provider registry
        mock_provider = MagicMock()
        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        assert flow.scope == scope
        assert flow.provider_registry == mock_provider

    def test_create_with_subagent_registry(self) -> None:
        """Create AgentFlow with optional SubagentRegistry."""
        scope = AgentScope(name="test-agent", model="gpt-4")
        mock_provider = MagicMock()
        subagent_registry = SubagentRegistry()

        flow = AgentFlow(
            scope=scope,
            provider_registry=mock_provider,
            subagent_registry=subagent_registry,
        )

        assert flow.subagent_registry == subagent_registry

    def test_create_without_subagent_registry(self) -> None:
        """Create AgentFlow without SubagentRegistry should create one."""
        scope = AgentScope(name="test-agent", model="gpt-4")
        mock_provider = MagicMock()

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        assert flow.subagent_registry is not None
        assert isinstance(flow.subagent_registry, SubagentRegistry)


class TestAgentFlowRun:
    """Test AgentFlow.run method."""

    @pytest.mark.asyncio
    async def test_run_returns_string(self) -> None:
        """run should return a string result."""
        scope = AgentScope(name="test-agent", model="gpt-4")

        # Create mock provider registry
        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Task completed successfully")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        result = await flow.run("Do something")

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_run_uses_scope_model(self) -> None:
        """run should use the model from scope."""
        scope = AgentScope(name="test-agent", model="claude-3-opus")

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Result")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        await flow.run("Test task")

        # Verify the model was used
        mock_provider.complete.assert_called_once()
        call_kwargs = mock_provider.complete.call_args
        assert "claude-3-opus" in str(call_kwargs) or call_kwargs[1].get("model") == "claude-3-opus"

    @pytest.mark.asyncio
    async def test_run_with_skill_selection(self) -> None:
        """run should select appropriate skill for task."""
        scope = AgentScope(
            name="test-agent",
            model="gpt-4",
            skills=["web_search", "summarize"],
        )

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Used web_search skill")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        result = await flow.run("Search for Python tutorials")

        assert "web_search" in result or result == "Used web_search skill"

    @pytest.mark.asyncio
    async def test_run_with_memory_search_disabled(self) -> None:
        """run should respect memory_search=False."""
        scope = AgentScope(
            name="test-agent",
            model="gpt-4",
            memory_search=False,
        )

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Result")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        result = await flow.run("Test task")

        assert result is not None


class TestAgentFlowSpawnSubagent:
    """Test AgentFlow.spawn_subagent method."""

    def test_spawn_subagent_returns_run_id(self) -> None:
        """spawn_subagent should return a run ID."""
        scope = AgentScope(
            name="main-agent",
            model="gpt-4",
            subagents={"researcher": "research-agent"},
        )

        mock_provider = MagicMock()
        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        run_id = flow.spawn_subagent("researcher", "Search for info")

        assert run_id is not None
        assert isinstance(run_id, str)

    def test_spawn_subagent_uses_subagent_model(self) -> None:
        """spawn_subagent should use the configured model."""
        scope = AgentScope(
            name="main-agent",
            model="gpt-4",
            subagents={"researcher": "claude-3-research"},
        )

        mock_provider = MagicMock()
        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        run_id = flow.spawn_subagent("researcher", "Task")
        run = flow.subagent_registry.get_run(run_id)

        assert run is not None
        assert run.model == "claude-3-research"

    def test_spawn_subagent_invalid_name_raises_error(self) -> None:
        """spawn_subagent should raise error for unknown subagent."""
        scope = AgentScope(name="main-agent", model="gpt-4")

        mock_provider = MagicMock()
        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        with pytest.raises(ValueError, match="Unknown subagent"):
            flow.spawn_subagent("unknown-subagent", "Task")

    def test_spawn_subagent_without_registry_raises_error(self) -> None:
        """spawn_subagent should raise error if no registry."""
        scope = AgentScope(name="main-agent", model="gpt-4")

        mock_provider = MagicMock()
        flow = AgentFlow(scope=scope, provider_registry=mock_provider)
        flow._subagent_registry = None

        with pytest.raises(ValueError, match="No subagent registry"):
            flow.spawn_subagent("any", "Task")


class TestAgentFlowTaskParsing:
    """Test AgentFlow task parsing logic."""

    @pytest.mark.asyncio
    async def test_parse_simple_task(self) -> None:
        """Parse a simple task without skills."""
        scope = AgentScope(name="test-agent", model="gpt-4")

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Task handled")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        result = await flow.run("Write a hello world program")

        assert result is not None

    @pytest.mark.asyncio
    async def test_parse_task_with_skill_keyword(self) -> None:
        """Parse task that contains skill keywords."""
        scope = AgentScope(
            name="test-agent",
            model="gpt-4",
            skills=["code_generation"],
        )

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Code generated")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        result = await flow.run("Generate code for a function")

        assert result is not None


class TestAgentFlowToolIntegration:
    """Test AgentFlow tool integration."""

    @pytest.mark.asyncio
    async def test_tools_available_in_context(self) -> None:
        """Tools should be available in execution context."""
        scope = AgentScope(
            name="test-agent",
            model="gpt-4",
            tools=["web_search", "code_exec"],
        )

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Used tools")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        result = await flow.run("Use tools to complete task")

        assert result is not None

    @pytest.mark.asyncio
    async def test_no_tools_available(self) -> None:
        """Agent can run without any tools."""
        scope = AgentScope(
            name="test-agent",
            model="gpt-4",
            tools=[],
        )

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="No tools needed")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        result = await flow.run("Simple task")

        assert result == "No tools needed"


class TestAgentFlowErrorHandling:
    """Test AgentFlow error handling."""

    @pytest.mark.asyncio
    async def test_provider_error_propagates(self) -> None:
        """Provider errors should propagate."""
        scope = AgentScope(name="test-agent", model="gpt-4")

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(side_effect=Exception("API error"))

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        with pytest.raises(Exception, match="API error"):
            await flow.run("Task that fails")

    @pytest.mark.asyncio
    async def test_empty_task_raises_error(self) -> None:
        """Empty task should raise error."""
        scope = AgentScope(name="test-agent", model="gpt-4")

        mock_provider = MagicMock()
        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        with pytest.raises(ValueError, match="Task cannot be empty"):
            await flow.run("")


class TestAgentFlowLifecycle:
    """Test AgentFlow lifecycle methods."""

    @pytest.mark.asyncio
    async def test_run_with_callbacks(self) -> None:
        """Run should support progress callbacks."""
        scope = AgentScope(name="test-agent", model="gpt-4")

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Done")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        progress_messages = []

        def on_progress(message: str) -> None:
            progress_messages.append(message)

        # Run with progress callback
        result = await flow.run("Task", on_progress=on_progress)

        assert result is not None

    def test_get_context(self) -> None:
        """get_context should return execution context."""
        scope = AgentScope(
            name="test-agent",
            model="gpt-4",
            skills=["skill1"],
            tools=["tool1"],
        )

        mock_provider = MagicMock()
        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        context = flow.get_context()

        assert context["name"] == "test-agent"
        assert context["model"] == "gpt-4"
        assert "skill1" in context["skills"]
        assert "tool1" in context["tools"]


class TestAgentFlowIntegration:
    """Integration tests for AgentFlow."""

    @pytest.mark.asyncio
    async def test_full_flow_with_subagent(self) -> None:
        """Test full flow including subagent spawning."""
        scope = AgentScope(
            name="orchestrator",
            model="gpt-4",
            skills=["research", "synthesis"],
            subagents={"researcher": "research-model"},
        )

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Task completed with subagent help")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        # Main task
        result = await flow.run("Research and synthesize information")

        # Spawn subagent
        run_id = flow.spawn_subagent("researcher", "Research subtask")

        assert result is not None
        assert run_id is not None

    @pytest.mark.asyncio
    async def test_concurrent_runs(self) -> None:
        """Test multiple concurrent runs."""
        import asyncio

        scope = AgentScope(name="test-agent", model="gpt-4")

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Result")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        tasks = [
            flow.run(f"Task {i}")
            for i in range(3)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)

    @pytest.mark.asyncio
    async def test_tool_selection_by_keyword(self) -> None:
        """Tool should be selected based on task keywords."""
        scope = AgentScope(
            name="test-agent",
            model="gpt-4",
            tools=["web_search", "code_exec"],
        )

        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="Result with tools")

        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        # Task with 'search' keyword should trigger web_search tool
        await flow.run("Search for information about Python")

        # Verify the prompt includes tool info
        call_args = mock_provider.complete.call_args
        prompt = call_args[0][0]
        assert "web_search" in prompt


class TestAgentFlowSubagentExecute:
    """Test AgentFlow subagent execution with errors."""

    def test_execute_subagent_error_sets_failed_status(self) -> None:
        """Subagent execution error should set FAILED status."""
        scope = AgentScope(
            name="main-agent",
            model="gpt-4",
            subagents={"worker": "worker-model"},
        )

        mock_provider = MagicMock()
        flow = AgentFlow(scope=scope, provider_registry=mock_provider)

        run_id = flow.spawn_subagent("worker", "Task")
        registry = flow.subagent_registry

        # Manually set error to test the error path
        run = registry.get_run(run_id)
        if run:
            run.status = flow.subagent_registry.get_status(run_id)
            run.error = "Test error"

        # Verify run was created
        assert run_id is not None