"""E2E Tests for LLM Multi-Provider Integration - Extended Scenarios.

These tests cover:
- Real-world fallback chain scenarios with simulated failures
- Capability-based model selection with complete_with_capability
- Configuration-driven integration tests
- Error recovery and resilience testing
"""

import os
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from markwritter.agent.flow import AgentFlow
from markwritter.agent.provider import ProviderRegistry as AgentProviderRegistry
from markwritter.agent.scope import AgentScope
from markwritter.agent.subagent import SubagentRegistry, SubagentStatus
from markwritter.llm_client import LLMClient, LLMError, MemoryCache
from markwritter.model_router import ModelRouter, RoutingRule
from markwritter.models import (
    CacheConfig,
    GlobalConfig,
    LLMConfig,
    ModelCapability,
    ModelDefinition,
    ProviderConfig,
)
from markwritter.provider_registry import ModelInfo, ProviderRegistry


# =============================================================================
# Mock Providers for Testing Fallback Chains
# =============================================================================


class FailingMockProvider:
    """Mock provider that simulates failures for testing fallback chains."""

    def __init__(
        self,
        fail_models: Optional[list[str]] = None,
        success_response: str = "Success response",
    ) -> None:
        """Initialize with models that should fail.

        Args:
            fail_models: List of model names that should fail
            success_response: Response to return for successful calls
        """
        self.fail_models = fail_models or []
        self.success_response = success_response
        self.call_history: list[tuple[str, str]] = []  # (model, prompt)

    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Return response or raise exception for failing models."""
        model_name = model or "default"
        self.call_history.append((model_name, prompt[:50]))

        if model_name in self.fail_models:
            raise Exception(f"Simulated failure for model: {model_name}")

        return f"[{model_name}] {self.success_response}"

    def chat_complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Return response or raise exception for failing models."""
        model_name = model or "default"
        self.call_history.append((model_name, "chat"))

        if model_name in self.fail_models:
            raise Exception(f"Simulated failure for model: {model_name}")

        return f"[{model_name}] Chat response"


class ConfigurableMockRegistry:
    """Configurable mock registry for testing capability-based selection."""

    def __init__(self, models_by_capability: dict[str, list[ModelInfo]]) -> None:
        """Initialize with pre-configured models by capability.

        Args:
            models_by_capability: Dict mapping capability to list of ModelInfo
        """
        self._models_by_capability = models_by_capability
        self._all_models: dict[str, ModelInfo] = {}
        for models in models_by_capability.values():
            for m in models:
                self._all_models[m.full_name] = m
                self._all_models[m.model_id] = m

    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get model info by name."""
        return self._all_models.get(model_name)

    def get_models_by_capability(self, capability: str) -> list[ModelInfo]:
        """Get models with specific capability."""
        return self._models_by_capability.get(capability, [])


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def production_like_config() -> LLMConfig:
    """Create a production-like LLM configuration."""
    return LLMConfig(
        default_model="openai/gpt-4o",
        timeout=30,
        max_retries=2,
        temperature=0.1,
        providers=[
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                is_default=True,
                models=[
                    ModelDefinition(
                        id="gpt-4o",
                        name="GPT-4o",
                        capabilities=ModelCapability(vision=True, tools=True, streaming=True),
                        context_window=128000,
                        max_tokens=4096,
                    ),
                    ModelDefinition(
                        id="gpt-4o-mini",
                        name="GPT-4o Mini",
                        capabilities=ModelCapability(vision=False, tools=True, streaming=True),
                        context_window=128000,
                        max_tokens=4096,
                    ),
                    ModelDefinition(
                        id="gpt-3.5-turbo",
                        name="GPT-3.5 Turbo",
                        capabilities=ModelCapability(vision=False, tools=False, streaming=True),
                        context_window=16000,
                        max_tokens=4096,
                    ),
                ],
            ),
            ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                models=[
                    ModelDefinition(
                        id="claude-3-opus",
                        name="Claude 3 Opus",
                        capabilities=ModelCapability(vision=True, tools=True, streaming=True),
                        context_window=200000,
                        max_tokens=4096,
                    ),
                    ModelDefinition(
                        id="claude-3-sonnet",
                        name="Claude 3 Sonnet",
                        capabilities=ModelCapability(vision=True, tools=True, streaming=True),
                        context_window=200000,
                        max_tokens=4096,
                    ),
                ],
            ),
            ProviderConfig(
                name="qwen",
                provider_type="openai-compatible",
                api_key_env="QWEN_API_KEY",
                base_url="https://api.qwen.ai/v1",
                models=[
                    ModelDefinition(
                        id="qwen3.5-plus",
                        name="Qwen 3.5 Plus",
                        capabilities=ModelCapability(vision=False, tools=False, streaming=True),
                        context_window=32000,
                        max_tokens=4096,
                    ),
                    ModelDefinition(
                        id="qwen-vl-plus",
                        name="Qwen VL Plus",
                        capabilities=ModelCapability(vision=True, tools=False, streaming=True),
                        context_window=32000,
                        max_tokens=4096,
                    ),
                ],
            ),
        ],
        fallback_chain=[
            "openai/gpt-4o",
            "anthropic/claude-3-opus",
            "qwen/qwen3.5-plus",
            "openai/gpt-4o-mini",
        ],
    )


@pytest.fixture
def production_registry(production_like_config: LLMConfig) -> ProviderRegistry:
    """Create registry with production-like configuration."""
    return ProviderRegistry(production_like_config)


# =============================================================================
# E2E Test: Fallback Chain with Simulated Failures
# =============================================================================


class TestFallbackChainWithFailures:
    """E2E tests for fallback chain behavior with simulated failures."""

    def test_fallback_to_second_model_on_primary_failure(
        self, production_like_config: LLMConfig, production_registry: ProviderRegistry
    ) -> None:
        """Test that fallback activates when primary model fails."""
        client = LLMClient(config=production_like_config, registry=production_registry)

        # Mock litellm to fail on first model, succeed on second
        with patch("litellm.completion") as mock_completion:
            # First call fails, second succeeds
            mock_completion.side_effect = [
                Exception("Primary model unavailable"),
                MagicMock(choices=[MagicMock(message=MagicMock(content="Fallback response"))]),
            ]

            result = client.complete(
                "Test prompt",
                model="openai/gpt-4o",
                fallback_models=["anthropic/claude-3-opus"],
            )

            assert result == "Fallback response"
            assert mock_completion.call_count == 2

    def test_fallback_chain_exhaustion_raises_error(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test that error is raised when all fallbacks fail."""
        client = LLMClient(config=production_like_config)

        with patch("litellm.completion") as mock_completion:
            # All calls fail
            mock_completion.side_effect = Exception("All models unavailable")

            with pytest.raises(LLMError) as exc_info:
                client.complete(
                    "Test prompt",
                    model="openai/gpt-4o",
                    fallback_models=["anthropic/claude-3-opus", "qwen/qwen3.5-plus"],
                )

            assert "All models in fallback chain failed" in str(exc_info.value)

    def test_fallback_chain_respects_retry_count(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test that each model in chain is retried appropriately."""
        client = LLMClient(config=production_like_config)

        with patch("litellm.completion") as mock_completion:
            mock_completion.side_effect = Exception("Model overloaded")

            with pytest.raises(LLMError):
                client.complete(
                    "Test prompt",
                    model="openai/gpt-4o",
                    fallback_models=["anthropic/claude-3-opus"],
                )

            # Each model should be tried (max_retries + 1) times
            # max_retries=2, so 3 attempts per model, 2 models = 6 total
            expected_calls = (production_like_config.max_retries + 1) * 2
            assert mock_completion.call_count == expected_calls

    def test_fallback_chain_with_config_defined_chain(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test using fallback chain defined in config."""
        client = LLMClient(config=production_like_config)

        with patch("litellm.completion") as mock_completion:
            # First two models fail, third succeeds
            mock_completion.side_effect = [
                Exception("GPT-4o unavailable"),
                Exception("Claude unavailable"),
                MagicMock(choices=[MagicMock(message=MagicMock(content="Qwen response"))]),
            ]

            result = client.complete(
                "Test prompt",
                model="openai/gpt-4o",
                fallback_models=production_like_config.fallback_chain[1:],
            )

            assert result == "Qwen response"
            assert mock_completion.call_count == 3

    def test_fallback_preserves_model_order(
        self, production_like_config: LLMConfig, production_registry: ProviderRegistry
    ) -> None:
        """Test that fallback chain preserves specified order."""
        client = LLMClient(config=production_like_config, registry=production_registry)

        fallback_order = ["anthropic/claude-3-opus", "qwen/qwen3.5-plus", "openai/gpt-4o-mini"]
        chain = client._get_fallback_chain("openai/gpt-4o", fallback_models=fallback_order)

        # Verify order
        assert chain[0] == "openai/gpt-4o"
        assert chain[1] == "anthropic/claude-3-opus"
        assert chain[2] == "qwen/qwen3.5-plus"
        assert chain[3] == "openai/gpt-4o-mini"


# =============================================================================
# E2E Test: Capability-Based Model Selection
# =============================================================================


class TestCapabilityBasedSelection:
    """E2E tests for capability-based model selection."""

    def test_complete_with_capability_selects_vision_model(
        self, production_like_config: LLMConfig, production_registry: ProviderRegistry
    ) -> None:
        """Test that complete_with_capability selects a model with vision capability."""
        client = LLMClient(config=production_like_config, registry=production_registry)

        with patch("litellm.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Vision analysis result"))]
            )

            result = client.complete_with_capability(
                "Describe this image",
                required_capability="vision",
            )

            assert result == "Vision analysis result"

            # Verify a vision-capable model was used
            call_args = mock_completion.call_args
            model_used = call_args.kwargs["model"]
            assert model_used in [
                "openai/gpt-4o",
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "qwen/qwen-vl-plus",
            ]

    def test_complete_with_capability_fallback_within_capability(
        self, production_like_config: LLMConfig, production_registry: ProviderRegistry
    ) -> None:
        """Test fallback to another vision-capable model on failure."""
        client = LLMClient(config=production_like_config, registry=production_registry)

        with patch("litellm.completion") as mock_completion:
            # First vision model fails, second succeeds
            mock_completion.side_effect = [
                Exception("Vision model A failed"),
                MagicMock(choices=[MagicMock(message=MagicMock(content="Vision model B result"))]),
            ]

            result = client.complete_with_capability(
                "Analyze image",
                required_capability="vision",
            )

            assert result == "Vision model B result"
            assert mock_completion.call_count == 2

    def test_complete_with_capability_no_capable_model_raises_error(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test error when no model has required capability."""
        # Create registry with no vision models
        config = LLMConfig(
            providers=[
                ProviderConfig(
                    name="test",
                    provider_type="openai-compatible",
                    api_key_env="TEST_KEY",
                    models=[
                        ModelDefinition(
                            id="text-only",
                            capabilities=ModelCapability(vision=False, tools=False),
                        )
                    ],
                )
            ]
        )
        registry = ProviderRegistry(config)
        client = LLMClient(config=config, registry=registry)

        with pytest.raises(LLMError) as exc_info:
            client.complete_with_capability(
                "Process image",
                required_capability="vision",
            )

        assert "No model found with capability: vision" in str(exc_info.value)

    def test_complete_with_capability_no_registry_raises_error(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test error when trying capability selection without registry."""
        client = LLMClient(config=production_like_config, registry=None)

        with pytest.raises(LLMError) as exc_info:
            client.complete_with_capability(
                "Test prompt",
                required_capability="vision",
            )

        assert "Registry required" in str(exc_info.value)

    def test_complete_with_capability_explicit_model_overrides(
        self, production_like_config: LLMConfig, production_registry: ProviderRegistry
    ) -> None:
        """Test that explicit model parameter overrides capability selection."""
        client = LLMClient(config=production_like_config, registry=production_registry)

        with patch("litellm.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Explicit model response"))]
            )

            result = client.complete_with_capability(
                "Test prompt",
                required_capability="vision",
                model="qwen/qwen3.5-plus",  # Non-vision model
            )

            assert result == "Explicit model response"

            # Verify the explicit model was used, not capability-selected one
            call_args = mock_completion.call_args
            assert call_args.kwargs["model"] == "qwen/qwen3.5-plus"

    def test_list_models_by_capability(
        self, production_registry: ProviderRegistry
    ) -> None:
        """Test listing models by specific capability."""
        vision_models = production_registry.get_models_by_capability("vision")
        tool_models = production_registry.get_models_by_capability("tools")
        streaming_models = production_registry.get_models_by_capability("streaming")

        # Verify vision models
        vision_names = [m.full_name for m in vision_models]
        assert "openai/gpt-4o" in vision_names
        assert "anthropic/claude-3-opus" in vision_names
        assert "qwen/qwen-vl-plus" in vision_names
        assert "qwen/qwen3.5-plus" not in vision_names  # No vision

        # Verify tool models
        tool_names = [m.full_name for m in tool_models]
        assert "openai/gpt-4o" in tool_names
        assert "anthropic/claude-3-opus" in tool_names
        assert "qwen/qwen3.5-plus" not in tool_names  # No tools

        # Verify streaming models (all should have it)
        # Count: gpt-4o, gpt-4o-mini, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet, qwen3.5-plus, qwen-vl-plus = 7
        assert len(streaming_models) == 7  # All models


# =============================================================================
# E2E Test: Model Router with Real-World Patterns
# =============================================================================


class TestModelRouterRealWorldPatterns:
    """E2E tests for model router with realistic file patterns."""

    @pytest.fixture
    def production_router(self) -> ModelRouter:
        """Create a router with production-like routing rules."""
        rules = [
            # Code files -> GPT-4o (best for coding)
            RoutingRule(
                pattern="**/src/**/*.py",
                model="openai/gpt-4o",
                task_types=("coding", "debugging", "refactoring"),
            ),
            RoutingRule(
                pattern="**/src/**/*.ts",
                model="openai/gpt-4o",
                task_types=("coding", "debugging", "refactoring"),
            ),
            # Documentation -> Claude (best for writing)
            RoutingRule(
                pattern="**/docs/**/*.md",
                model="anthropic/claude-3-opus",
                task_types=("writing", "documentation"),
            ),
            # Drafts -> Claude
            RoutingRule(
                pattern="**/drafts/**",
                model="anthropic/claude-3-opus",
                task_types=("writing",),
            ),
            # Tests -> GPT-4o Mini (faster, cheaper)
            RoutingRule(
                pattern="**/tests/**/*.py",
                model="openai/gpt-4o-mini",
                task_types=("testing", "coding"),
            ),
            # Config files -> GPT-4o Mini
            RoutingRule(
                pattern="**/*.yaml",
                model="openai/gpt-4o-mini",
            ),
            RoutingRule(
                pattern="**/*.json",
                model="openai/gpt-4o-mini",
            ),
            # All other markdown -> Qwen (cost-effective)
            RoutingRule(
                pattern="**/*.md",
                model="qwen/qwen3.5-plus",
            ),
        ]
        return ModelRouter(rules=rules, default_model="qwen/qwen3.5-plus")

    def test_route_python_source_file(self, production_router: ModelRouter) -> None:
        """Test routing for Python source files."""
        # Source file with coding task
        model = production_router.get_model("src/api/handlers.py", task_type="coding")
        assert model == "openai/gpt-4o"

        # Nested source file
        model = production_router.get_model("project/src/services/auth/user.py", task_type="debugging")
        assert model == "openai/gpt-4o"

    def test_route_documentation_file(self, production_router: ModelRouter) -> None:
        """Test routing for documentation files."""
        model = production_router.get_model("docs/api/reference.md", task_type="documentation")
        assert model == "anthropic/claude-3-opus"

        model = production_router.get_model("docs/getting-started.md", task_type="writing")
        assert model == "anthropic/claude-3-opus"

    def test_route_test_file(self, production_router: ModelRouter) -> None:
        """Test routing for test files."""
        model = production_router.get_model("tests/unit/test_api.py", task_type="testing")
        assert model == "openai/gpt-4o-mini"

        model = production_router.get_model("tests/integration/test_flow.py", task_type="coding")
        assert model == "openai/gpt-4o-mini"

    def test_route_config_file(self, production_router: ModelRouter) -> None:
        """Test routing for configuration files."""
        model = production_router.get_model("config/settings.yaml")
        assert model == "openai/gpt-4o-mini"

        model = production_router.get_model("package.json")
        assert model == "openai/gpt-4o-mini"

    def test_route_draft_file(self, production_router: ModelRouter) -> None:
        """Test routing for draft files."""
        model = production_router.get_model("drafts/blog-post.md", task_type="writing")
        assert model == "anthropic/claude-3-opus"

        # Draft without task type falls through to .md rule
        model = production_router.get_model("drafts/blog-post.md")
        assert model == "qwen/qwen3.5-plus"

    def test_route_unknown_file_uses_default(self, production_router: ModelRouter) -> None:
        """Test routing for unknown file types uses default."""
        model = production_router.get_model("data/export.csv")
        assert model == "qwen/qwen3.5-plus"

        model = production_router.get_model("assets/logo.png")
        assert model == "qwen/qwen3.5-plus"

    def test_route_with_task_type_filtering(self, production_router: ModelRouter) -> None:
        """Test that task type filtering works correctly."""
        # Python file with writing task (not matching) falls to .md rule which doesn't match
        # then falls to default
        model = production_router.get_model("src/utils.py", task_type="writing")
        # No matching rule for writing in src, falls through to default
        assert model == "qwen/qwen3.5-plus"


# =============================================================================
# E2E Test: Agent Flow with Multi-Provider
# =============================================================================


class TestAgentFlowMultiProvider:
    """E2E tests for agent flow with multi-provider integration."""

    @pytest.fixture
    def mock_provider(self) -> MagicMock:
        """Create a mock LLM provider."""
        provider = MagicMock()
        provider.complete.return_value = "Mock agent response"
        return provider

    @pytest.fixture
    def multi_model_scope(self) -> AgentScope:
        """Create an agent scope with multiple model options."""
        return AgentScope(
            name="multi-model-agent",
            model="openai/gpt-4o",
            skills=["web_search", "summarize", "analyze", "code_generation"],
            tools=["web_search", "code_exec"],
            subagents={
                "researcher": "anthropic/claude-3-opus",
                "coder": "openai/gpt-4o",
                "writer": "anthropic/claude-3-sonnet",
            },
        )

    def test_agent_uses_primary_model(
        self, mock_provider: MagicMock, multi_model_scope: AgentScope
    ) -> None:
        """Test that agent uses the primary model from scope."""
        registry = AgentProviderRegistry(default_provider=mock_provider)
        flow = AgentFlow(scope=multi_model_scope, provider_registry=registry)

        # Execute should use the scope's model
        flow._provider_registry.complete("Test prompt", model="openai/gpt-4o")

        mock_provider.complete.assert_called_once()

    def test_agent_subagent_model_configuration(
        self, multi_model_scope: AgentScope
    ) -> None:
        """Test that subagent models are correctly configured."""
        assert multi_model_scope.get_subagent_model("researcher") == "anthropic/claude-3-opus"
        assert multi_model_scope.get_subagent_model("coder") == "openai/gpt-4o"
        assert multi_model_scope.get_subagent_model("writer") == "anthropic/claude-3-sonnet"

    def test_agent_spawn_subagent_with_correct_model(
        self, mock_provider: MagicMock, multi_model_scope: AgentScope
    ) -> None:
        """Test spawning subagent with correct model assignment."""
        registry = AgentProviderRegistry(default_provider=mock_provider)
        flow = AgentFlow(scope=multi_model_scope, provider_registry=registry)

        # Spawn researcher subagent
        run_id = flow.spawn_subagent("researcher", "Research AI trends")

        assert run_id is not None

        # Check the subagent run has correct model
        run = flow.subagent_registry.get_run(run_id)
        assert run is not None
        assert run.model == "anthropic/claude-3-opus"

    def test_agent_skill_detection_in_task(
        self, mock_provider: MagicMock, multi_model_scope: AgentScope
    ) -> None:
        """Test that agent correctly detects skills from task description."""
        registry = AgentProviderRegistry(default_provider=mock_provider)
        flow = AgentFlow(scope=multi_model_scope, provider_registry=registry)

        # Task with skill keywords
        # Note: skill detection uses skill.replace("_", " ") to match
        # e.g., "web_search" -> "web search" (must appear as substring)
        plan = flow._parse_task("Perform a web search for Python tutorials and summarize the results")

        # "web search" should be detected from "web search" in task
        assert "web_search" in plan["skills"]
        # "summarize" should be detected from "summarize" in task
        assert "summarize" in plan["skills"]

    def test_agent_tool_detection_in_task(
        self, mock_provider: MagicMock, multi_model_scope: AgentScope
    ) -> None:
        """Test that agent correctly detects tools from task description."""
        registry = AgentProviderRegistry(default_provider=mock_provider)
        flow = AgentFlow(scope=multi_model_scope, provider_registry=registry)

        # Task with tool keywords
        plan = flow._parse_task("Execute a Python script to process data")

        assert "code_exec" in plan["tools"]


# =============================================================================
# E2E Test: Cache Integration
# =============================================================================


class TestCacheIntegration:
    """E2E tests for cache integration with LLM client."""

    def test_cache_hits_same_prompt_same_model(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test that cache returns same result for identical prompt/model."""
        cache_config = CacheConfig(enabled=True, max_size=100, ttl_seconds=3600)
        global_config = GlobalConfig(llm=production_like_config, cache=cache_config)

        with patch("markwritter.llm_client.get_config", return_value=global_config):
            client = LLMClient(config=production_like_config)

            with patch("litellm.completion") as mock_completion:
                mock_completion.return_value = MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Cached response"))]
                )

                # First call
                result1 = client.complete("Same prompt", model="openai/gpt-4o")
                # Second call (should hit cache)
                result2 = client.complete("Same prompt", model="openai/gpt-4o")

                assert result1 == result2
                # Only called once due to cache
                mock_completion.assert_called_once()

    def test_cache_miss_different_model(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test that cache misses for different model."""
        cache_config = CacheConfig(enabled=True, max_size=100, ttl_seconds=3600)
        global_config = GlobalConfig(llm=production_like_config, cache=cache_config)

        with patch("markwritter.llm_client.get_config", return_value=global_config):
            client = LLMClient(config=production_like_config)

            with patch("litellm.completion") as mock_completion:
                mock_completion.return_value = MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Response"))]
                )

                # Same prompt, different model
                client.complete("Same prompt", model="openai/gpt-4o")
                client.complete("Same prompt", model="anthropic/claude-3-opus")

                # Called twice (different cache keys)
                assert mock_completion.call_count == 2

    def test_cache_disabled(self, production_like_config: LLMConfig) -> None:
        """Test behavior when cache is disabled."""
        cache_config = CacheConfig(enabled=False)
        global_config = GlobalConfig(llm=production_like_config, cache=cache_config)

        with patch("markwritter.llm_client.get_config", return_value=global_config):
            client = LLMClient(config=production_like_config)

            with patch("litellm.completion") as mock_completion:
                mock_completion.return_value = MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Response"))]
                )

                # Multiple calls with same prompt
                client.complete("Same prompt", model="openai/gpt-4o")
                client.complete("Same prompt", model="openai/gpt-4o")

                # Called twice (no caching)
                assert mock_completion.call_count == 2

    def test_cache_stats(self, production_like_config: LLMConfig) -> None:
        """Test cache statistics."""
        cache_config = CacheConfig(enabled=True, max_size=100, ttl_seconds=3600)
        global_config = GlobalConfig(llm=production_like_config, cache=cache_config)

        with patch("markwritter.llm_client.get_config", return_value=global_config):
            client = LLMClient(config=production_like_config)

            stats = client.get_cache_stats()
            assert stats["max_size"] == 100
            assert stats["size"] == 0


# =============================================================================
# E2E Test: Error Recovery
# =============================================================================


class TestErrorRecovery:
    """E2E tests for error recovery and resilience."""

    def test_retry_on_transient_error(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test that client retries on transient errors."""
        client = LLMClient(config=production_like_config)

        with patch("litellm.completion") as mock_completion:
            # Fail twice, succeed on third
            mock_completion.side_effect = [
                Exception("Temporary error"),
                Exception("Another temporary error"),
                MagicMock(choices=[MagicMock(message=MagicMock(content="Success"))]),
            ]

            result = client.complete("Test prompt", model="openai/gpt-4o")

            assert result == "Success"
            assert mock_completion.call_count == 3

    def test_timeout_error_handling(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test handling of timeout errors."""
        client = LLMClient(config=production_like_config)

        with patch("litellm.completion") as mock_completion:
            mock_completion.side_effect = TimeoutError("Request timed out")

            with pytest.raises(LLMError):
                client.complete("Test prompt", model="openai/gpt-4o")

    def test_invalid_api_key_error(
        self, production_registry: ProviderRegistry
    ) -> None:
        """Test handling of missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            api_key = production_registry.get_api_key("openai")
            assert api_key is None

            api_key = production_registry.get_api_key("anthropic")
            assert api_key is None

    def test_graceful_handling_of_malformed_response(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test handling of malformed API response."""
        client = LLMClient(config=production_like_config)

        with patch("litellm.completion") as mock_completion:
            # Return response without choices
            mock_completion.return_value = MagicMock(choices=[])

            with pytest.raises((IndexError, LLMError)):
                client.complete("Test prompt", model="openai/gpt-4o")


# =============================================================================
# E2E Test: Provider Registry Edge Cases
# =============================================================================


class TestProviderRegistryEdgeCases:
    """E2E tests for provider registry edge cases."""

    def test_duplicate_model_id_across_providers(
        self, production_like_config: LLMConfig
    ) -> None:
        """Test handling of duplicate model IDs across providers."""
        # Add a provider with duplicate model ID
        config = LLMConfig(
            providers=[
                ProviderConfig(
                    name="provider1",
                    provider_type="openai-compatible",
                    api_key_env="KEY1",
                    models=[ModelDefinition(id="shared-model")],
                ),
                ProviderConfig(
                    name="provider2",
                    provider_type="openai-compatible",
                    api_key_env="KEY2",
                    models=[ModelDefinition(id="shared-model")],
                ),
            ]
        )

        registry = ProviderRegistry(config)

        # Should be able to get by full name
        model1 = registry.get_model("provider1/shared-model")
        assert model1 is not None

        model2 = registry.get_model("provider2/shared-model")
        assert model2 is not None

        # Short name returns first found
        model = registry.get_model("shared-model")
        assert model is not None

    def test_empty_provider_list(self) -> None:
        """Test registry with no providers."""
        registry = ProviderRegistry(LLMConfig())

        assert registry.list_providers() == []
        assert registry.list_models() == []
        assert registry.get_default_provider() is None

    def test_provider_with_no_models(self) -> None:
        """Test provider configuration with empty model list."""
        config = LLMConfig(
            providers=[
                ProviderConfig(
                    name="empty-provider",
                    provider_type="openai",
                    api_key_env="KEY",
                    models=[],
                )
            ]
        )

        registry = ProviderRegistry(config)

        assert registry.get_provider("empty-provider") is not None
        assert registry.list_models() == []

    def test_model_info_properties(
        self, production_registry: ProviderRegistry
    ) -> None:
        """Test ModelInfo property access."""
        model_info = production_registry.get_model_info("gpt-4o")

        assert model_info is not None
        assert model_info.model_id == "gpt-4o"
        assert model_info.full_name == "openai/gpt-4o"
        assert model_info.provider == "openai"
        assert "vision" in model_info.capabilities
        assert "tools" in model_info.capabilities
        assert model_info.context_window == 128000
        assert model_info.max_tokens == 4096


# =============================================================================
# E2E Test: Subagent Lifecycle
# =============================================================================


class TestSubagentLifecycle:
    """E2E tests for subagent lifecycle management."""

    def test_subagent_status_transitions(self) -> None:
        """Test subagent status transitions through lifecycle."""
        registry = SubagentRegistry()

        # Spawn -> IDLE
        run_id = registry.spawn("test-agent", "gpt-4o", "Test task")
        assert registry.get_status(run_id) == SubagentStatus.IDLE

        # Execute -> RUNNING -> COMPLETED
        registry.execute(run_id, "test_skill", {"param": "value"})
        assert registry.get_status(run_id) == SubagentStatus.COMPLETED

    def test_subagent_failure_status(self) -> None:
        """Test subagent status on failure."""
        registry = SubagentRegistry()
        run_id = registry.spawn("test", "gpt-4o", "Task")

        # Override execute to fail
        run = registry.get_run(run_id)
        assert run is not None

        # Manually set failed status (simulating error)
        from markwritter.agent.subagent import SubagentStatus
        run.status = SubagentStatus.FAILED
        run.error = "Simulated failure"

        assert registry.get_status(run_id) == SubagentStatus.FAILED
        assert run.error == "Simulated failure"

    def test_multiple_subagents_tracking(self) -> None:
        """Test tracking multiple concurrent subagents."""
        registry = SubagentRegistry()

        # Spawn multiple subagents
        ids = [
            registry.spawn("agent1", "gpt-4o", "Task 1"),
            registry.spawn("agent2", "claude-3-opus", "Task 2"),
            registry.spawn("agent3", "qwen3.5-plus", "Task 3"),
        ]

        # Execute first two
        registry.execute(ids[0], "skill1", {})
        registry.execute(ids[1], "skill2", {})

        # Check status distribution
        completed = registry.list_runs(status=SubagentStatus.COMPLETED)
        idle = registry.list_runs(status=SubagentStatus.IDLE)

        assert len(completed) == 2
        assert len(idle) == 1

    def test_subagent_cleanup_removes_run(self) -> None:
        """Test that cleanup removes run from registry."""
        registry = SubagentRegistry()
        run_id = registry.spawn("agent", "gpt-4o", "Task")

        assert registry.get_run(run_id) is not None

        registry.cleanup(run_id)

        assert registry.get_run(run_id) is None

    def test_subagent_announce(self) -> None:
        """Test progress announcement for subagent."""
        registry = SubagentRegistry()
        run_id = registry.spawn("agent", "gpt-4o", "Task")

        # Should not raise
        registry.announce(run_id, "Progress: 50%")

        # Invalid run ID should raise
        with pytest.raises(ValueError):
            registry.announce("invalid-id", "Progress")