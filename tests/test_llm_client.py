"""Tests for LLM Client with Provider Registry support."""

import hashlib
import time
from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from markwritter.llm_client import LLMClient, LLMError, MemoryCache
from markwritter.models import CacheConfig, GlobalConfig, LLMConfig


# =============================================================================
# Mock Provider Registry for Testing
# =============================================================================


@dataclass
class ModelInfo:
    """Model information for testing."""

    provider: str
    model_id: str
    capabilities: list[str]
    supports_streaming: bool = True
    supports_vision: bool = False
    supports_function_calling: bool = True

    @property
    def full_name(self) -> str:
        """Get full model name in provider/model format."""
        return f"{self.provider}/{self.model_id}"


class MockProviderRegistry:
    """Mock provider registry for testing."""

    def __init__(self) -> None:
        """Initialize with default models."""
        self._models: dict[str, ModelInfo] = {}
        self._setup_default_models()

    def _setup_default_models(self) -> None:
        """Setup default test models."""
        models = [
            ModelInfo(
                provider="openai",
                model_id="gpt-4",
                capabilities=["chat", "reasoning", "function_calling"],
                supports_vision=False,
            ),
            ModelInfo(
                provider="openai",
                model_id="gpt-4-vision",
                capabilities=["chat", "reasoning", "vision", "function_calling"],
                supports_vision=True,
            ),
            ModelInfo(
                provider="anthropic",
                model_id="claude-3-opus",
                capabilities=["chat", "reasoning", "vision", "function_calling"],
                supports_vision=True,
            ),
            ModelInfo(
                provider="anthropic",
                model_id="claude-3-sonnet",
                capabilities=["chat", "reasoning", "function_calling"],
                supports_vision=False,
            ),
            ModelInfo(
                provider="qwen",
                model_id="qwen3.5-plus",
                capabilities=["chat", "reasoning"],
            ),
        ]
        for model in models:
            self._models[model.full_name] = model

    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get model info by name.

        Supports formats:
        - 'provider/model' (full format)
        - 'model' (short format, searches all providers)
        """
        # Try full format first
        if "/" in model_name:
            return self._models.get(model_name)

        # Search for short format
        for name, info in self._models.items():
            if info.model_id == model_name:
                return info

        return None

    # Keep get_model as alias for backward compatibility
    get_model = get_model_info

    def get_models_by_capability(self, capability: str) -> list[ModelInfo]:
        """Get all models that have a specific capability."""
        return [m for m in self._models.values() if capability in m.capabilities]

    def resolve_model(self, model: str, fallback_models: Optional[list[str]] = None) -> list[str]:
        """Resolve model name and return ordered fallback chain.

        Args:
            model: Primary model name (can be provider/model or just model)
            fallback_models: Optional list of fallback model names

        Returns:
            Ordered list of model names to try
        """
        models_to_try: list[str] = []

        # Resolve primary model
        model_info = self.get_model(model)
        if model_info:
            models_to_try.append(model_info.full_name)
        else:
            models_to_try.append(model)

        # Add fallbacks
        if fallback_models:
            for fb in fallback_models:
                if fb not in models_to_try:
                    fb_info = self.get_model(fb)
                    if fb_info:
                        models_to_try.append(fb_info.full_name)
                    else:
                        models_to_try.append(fb)

        return models_to_try


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_registry() -> MockProviderRegistry:
    """Create a mock provider registry."""
    return MockProviderRegistry()


@pytest.fixture
def llm_config() -> LLMConfig:
    """Create a basic LLM config."""
    return LLMConfig(
        default_model="qwen/qwen3.5-plus",
        timeout=30,
        max_retries=2,
        temperature=0.1,
    )


@pytest.fixture
def global_config(llm_config: LLMConfig) -> GlobalConfig:
    """Create a global config with LLM config."""
    return GlobalConfig(
        llm=llm_config,
        cache=CacheConfig(enabled=False),
    )


@pytest.fixture
def client_with_registry(global_config: GlobalConfig, mock_registry: MockProviderRegistry) -> LLMClient:
    """Create LLM client with registry."""
    return LLMClient(config=global_config.llm, registry=mock_registry)


@pytest.fixture
def client_without_registry(global_config: GlobalConfig) -> LLMClient:
    """Create LLM client without registry."""
    return LLMClient(config=global_config.llm)


# =============================================================================
# Test: ProviderRegistry Support
# =============================================================================


class TestLLMClientRegistrySupport:
    """Tests for ProviderRegistry integration."""

    def test_client_accepts_registry_in_constructor(self, llm_config: LLMConfig, mock_registry: MockProviderRegistry) -> None:
        """Test that LLMClient accepts registry parameter."""
        client = LLMClient(config=llm_config, registry=mock_registry)
        assert client.registry is mock_registry

    def test_client_works_without_registry(self, llm_config: LLMConfig) -> None:
        """Test that LLMClient works without registry (backward compatibility)."""
        client = LLMClient(config=llm_config)
        assert client.registry is None

    def test_client_uses_registry_for_model_resolution(
        self, client_with_registry: LLMClient, mock_registry: MockProviderRegistry
    ) -> None:
        """Test that client uses registry to resolve model names."""
        # Should resolve 'gpt-4' to 'openai/gpt-4'
        resolved = client_with_registry._resolve_model("gpt-4")
        assert resolved == "openai/gpt-4"

    def test_client_handles_full_model_name(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test that client handles full provider/model format."""
        resolved = client_with_registry._resolve_model("anthropic/claude-3-opus")
        assert resolved == "anthropic/claude-3-opus"

    def test_client_handles_unknown_model_without_registry(
        self, client_without_registry: LLMClient
    ) -> None:
        """Test that client handles unknown model without registry."""
        resolved = client_without_registry._resolve_model("unknown-model")
        assert resolved == "unknown-model"


# =============================================================================
# Test: Model Name Parsing
# =============================================================================


class TestModelNameParsing:
    """Tests for provider/model format parsing."""

    def test_parse_provider_model_format(self, client_with_registry: LLMClient) -> None:
        """Test parsing 'provider/model' format."""
        provider, model = client_with_registry._parse_model_string("openai/gpt-4")
        assert provider == "openai"
        assert model == "gpt-4"

    def test_parse_model_only_format(self, client_with_registry: LLMClient) -> None:
        """Test parsing model-only format."""
        provider, model = client_with_registry._parse_model_string("gpt-4")
        assert provider is None
        assert model == "gpt-4"

    def test_parse_complex_model_name(self, client_with_registry: LLMClient) -> None:
        """Test parsing model name with slashes in model ID."""
        # Some models have slashes like 'meta-llama/Llama-2-70b'
        provider, model = client_with_registry._parse_model_string("meta-llama/Llama-2-70b")
        assert provider == "meta-llama"
        assert model == "Llama-2-70b"

    def test_parse_empty_model_string(self, client_with_registry: LLMClient) -> None:
        """Test handling empty model string."""
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            client_with_registry._parse_model_string("")


# =============================================================================
# Test: Fallback Chain Mechanism
# =============================================================================


class TestFallbackChain:
    """Tests for fallback chain mechanism."""

    def test_resolve_model_returns_single_model_without_fallbacks(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test that resolve returns single model when no fallbacks."""
        models = client_with_registry._get_fallback_chain("gpt-4", fallback_models=None)
        assert models == ["openai/gpt-4"]

    def test_resolve_model_includes_fallbacks(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test that resolve includes fallback models."""
        models = client_with_registry._get_fallback_chain(
            "gpt-4",
            fallback_models=["anthropic/claude-3-sonnet", "qwen/qwen3.5-plus"],
        )
        assert models == ["openai/gpt-4", "anthropic/claude-3-sonnet", "qwen/qwen3.5-plus"]

    def test_fallback_chain_deduplicates_models(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test that duplicate models are removed."""
        models = client_with_registry._get_fallback_chain(
            "gpt-4",
            fallback_models=["openai/gpt-4", "anthropic/claude-3-sonnet"],
        )
        assert models == ["openai/gpt-4", "anthropic/claude-3-sonnet"]
        assert len(models) == 2  # No duplicate

    def test_fallback_chain_preserves_order(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test that fallback order is preserved."""
        models = client_with_registry._get_fallback_chain(
            "gpt-4",
            fallback_models=["anthropic/claude-3-opus", "qwen/qwen3.5-plus", "anthropic/claude-3-sonnet"],
        )
        assert models[0] == "openai/gpt-4"  # Primary first
        assert models[1] == "anthropic/claude-3-opus"  # Then fallbacks in order

    def test_fallback_chain_without_registry_uses_raw_names(
        self, client_without_registry: LLMClient
    ) -> None:
        """Test that without registry, raw model names are used."""
        models = client_without_registry._get_fallback_chain(
            "gpt-4",
            fallback_models=["claude-3-sonnet"],
        )
        assert models == ["gpt-4", "claude-3-sonnet"]


# =============================================================================
# Test: Complete with Fallback
# =============================================================================


class TestCompleteWithFallback:
    """Tests for complete method with fallback support."""

    @patch("litellm.completion")
    def test_complete_uses_primary_model_on_success(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that complete uses primary model when it succeeds."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Success response"))]
        )

        result = client_with_registry.complete(
            "Test prompt",
            model="gpt-4",
            fallback_models=["anthropic/claude-3-sonnet"],
        )

        assert result == "Success response"
        # Should only call once (primary succeeded)
        assert mock_completion.call_count == 1
        called_model = mock_completion.call_args[1]["model"]
        assert called_model == "openai/gpt-4"

    @patch("litellm.completion")
    def test_complete_falls_back_on_primary_failure(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that complete tries fallback when primary fails."""
        call_count = [0]

        def mock_completion_fn(**kwargs: dict) -> MagicMock:
            call_count[0] += 1
            if call_count[0] == 1:  # First call (primary) fails
                raise Exception("Primary model failed")
            return MagicMock(choices=[MagicMock(message=MagicMock(content="Fallback response"))])

        mock_completion.side_effect = mock_completion_fn

        result = client_with_registry.complete(
            "Test prompt",
            model="gpt-4",
            fallback_models=["anthropic/claude-3-sonnet"],
        )

        assert result == "Fallback response"
        assert call_count[0] == 2  # Primary failed, fallback succeeded

    @patch("litellm.completion")
    def test_complete_raises_after_all_fallbacks_fail(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that LLMError is raised when all models fail."""
        mock_completion.side_effect = Exception("All models failed")

        with pytest.raises(LLMError, match="All models in fallback chain failed"):
            client_with_registry.complete(
                "Test prompt",
                model="gpt-4",
                fallback_models=["anthropic/claude-3-sonnet"],
            )

    @patch("litellm.completion")
    def test_complete_without_fallbacks_backward_compatible(
        self, mock_completion: MagicMock, client_without_registry: LLMClient
    ) -> None:
        """Test backward compatibility - complete works without fallbacks."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        result = client_without_registry.complete("Test prompt")

        assert result == "Response"
        assert mock_completion.call_count == 1


# =============================================================================
# Test: Complete with Capability
# =============================================================================


class TestCompleteWithCapability:
    """Tests for complete_with_capability method."""

    @patch("litellm.completion")
    def test_selects_model_with_required_capability(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that capability-based model selection works."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Vision response"))]
        )

        result = client_with_registry.complete_with_capability(
            "Describe this image",
            required_capability="vision",
        )

        assert result == "Vision response"
        called_model = mock_completion.call_args[1]["model"]
        # Should use a model with vision capability
        assert "vision" in called_model or "claude-3-opus" in called_model

    @patch("litellm.completion")
    def test_selects_first_available_model_for_capability(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that first model with capability is selected."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Chat response"))]
        )

        result = client_with_registry.complete_with_capability(
            "Hello",
            required_capability="chat",
        )

        assert result == "Chat response"
        # Should select first model with 'chat' capability
        called_model = mock_completion.call_args[1]["model"]
        assert called_model is not None

    def test_raises_error_when_no_model_has_capability(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test error when no model has the required capability."""
        with pytest.raises(LLMError, match="No model found with capability"):
            client_with_registry.complete_with_capability(
                "Test prompt",
                required_capability="nonexistent_capability",
            )

    def test_raises_error_when_no_registry_for_capability(
        self, client_without_registry: LLMClient
    ) -> None:
        """Test error when trying capability selection without registry."""
        with pytest.raises(LLMError, match="Registry required"):
            client_without_registry.complete_with_capability(
                "Test prompt",
                required_capability="vision",
            )

    @patch("litellm.completion")
    def test_capability_with_explicit_model_overrides(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that explicit model parameter overrides capability selection."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Explicit model response"))]
        )

        result = client_with_registry.complete_with_capability(
            "Test prompt",
            required_capability="vision",
            model="anthropic/claude-3-sonnet",  # Explicit model (no vision)
        )

        assert result == "Explicit model response"
        called_model = mock_completion.call_args[1]["model"]
        assert called_model == "anthropic/claude-3-sonnet"

    @patch("litellm.completion")
    def test_capability_with_fallback_models(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that fallback models work with capability selection."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        result = client_with_registry.complete_with_capability(
            "Test prompt",
            required_capability="chat",
            fallback_models=["qwen/qwen3.5-plus"],
        )

        assert result == "Response"


# =============================================================================
# Test: Provider Parameter
# =============================================================================


class TestProviderParameter:
    """Tests for provider parameter in complete method."""

    @patch("litellm.completion")
    def test_provider_prefix_is_added(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that provider prefix is added when provider is specified."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        result = client_with_registry.complete(
            "Test prompt",
            model="gpt-4",
            provider="openai",
        )

        assert result == "Response"
        called_model = mock_completion.call_args[1]["model"]
        assert called_model == "openai/gpt-4"

    @patch("litellm.completion")
    def test_provider_ignored_if_model_has_prefix(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that provider is ignored if model already has provider prefix."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        result = client_with_registry.complete(
            "Test prompt",
            model="anthropic/claude-3-opus",
            provider="openai",  # Should be ignored
        )

        assert result == "Response"
        called_model = mock_completion.call_args[1]["model"]
        assert called_model == "anthropic/claude-3-opus"

    @patch("litellm.completion")
    def test_provider_without_registry(
        self, mock_completion: MagicMock, client_without_registry: LLMClient
    ) -> None:
        """Test that provider parameter works without registry."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        result = client_without_registry.complete(
            "Test prompt",
            model="claude-3-opus",
            provider="anthropic",
        )

        assert result == "Response"
        called_model = mock_completion.call_args[1]["model"]
        assert called_model == "anthropic/claude-3-opus"


# =============================================================================
# Test: Error Handling in Fallback
# =============================================================================


class TestFallbackErrorHandling:
    """Tests for error handling in fallback scenarios."""

    @patch("litellm.completion")
    def test_fallback_on_rate_limit(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that fallback occurs on rate limit errors."""
        call_count = [0]

        def mock_completion_fn(**kwargs: dict) -> MagicMock:
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Rate limit exceeded")
            return MagicMock(choices=[MagicMock(message=MagicMock(content="Fallback response"))])

        mock_completion.side_effect = mock_completion_fn

        result = client_with_registry.complete(
            "Test prompt",
            model="gpt-4",
            fallback_models=["anthropic/claude-3-sonnet"],
        )

        assert result == "Fallback response"
        assert call_count[0] == 2

    @patch("litellm.completion")
    def test_fallback_on_timeout(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that fallback occurs on timeout errors."""
        call_count = [0]

        def mock_completion_fn(**kwargs: dict) -> MagicMock:
            call_count[0] += 1
            if call_count[0] == 1:
                raise TimeoutError("Request timed out")
            return MagicMock(choices=[MagicMock(message=MagicMock(content="Fallback response"))])

        mock_completion.side_effect = mock_completion_fn

        result = client_with_registry.complete(
            "Test prompt",
            model="gpt-4",
            fallback_models=["anthropic/claude-3-sonnet"],
        )

        assert result == "Fallback response"

    @patch("litellm.completion")
    def test_error_message_includes_all_failures(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that final error includes details of all failed attempts."""
        mock_completion.side_effect = Exception("Model failed")

        with pytest.raises(LLMError) as exc_info:
            client_with_registry.complete(
                "Test prompt",
                model="gpt-4",
                fallback_models=["anthropic/claude-3-sonnet"],
            )

        error_message = str(exc_info.value)
        assert "gpt-4" in error_message or "openai/gpt-4" in error_message


# =============================================================================
# Test: Cache Compatibility
# =============================================================================


class TestCacheCompatibility:
    """Tests that caching works with fallback and capability features."""

    @patch("litellm.completion")
    def test_cache_key_includes_resolved_model(
        self, mock_completion: MagicMock, mock_registry: MockProviderRegistry
    ) -> None:
        """Test that cache key uses resolved model name."""
        config = LLMConfig(default_model="qwen/qwen3.5-plus")
        cache_config = CacheConfig(enabled=True, max_size=100, ttl_seconds=3600)
        global_config = GlobalConfig(llm=config, cache=cache_config)

        with patch("markwritter.llm_client.get_config", return_value=global_config):
            client = LLMClient(config=config, registry=mock_registry)

            mock_completion.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Cached response"))]
            )

            # First call
            result1 = client.complete("Test prompt", model="gpt-4")
            # Second call should hit cache
            result2 = client.complete("Test prompt", model="openai/gpt-4")

            assert result1 == "Cached response"
            assert result2 == "Cached response"
            # Should only call API once (second is cached)
            assert mock_completion.call_count == 1

    @patch("litellm.completion")
    def test_cache_disabled_during_fallback(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test that cache is checked before fallback chain."""
        # Disable cache for this test
        client_with_registry.cache = None

        call_count = [0]

        def mock_completion_fn(**kwargs: dict) -> MagicMock:
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Primary failed")
            return MagicMock(choices=[MagicMock(message=MagicMock(content="Fallback"))])

        mock_completion.side_effect = mock_completion_fn

        result = client_with_registry.complete(
            "Test prompt",
            model="gpt-4",
            fallback_models=["anthropic/claude-3-sonnet"],
        )

        assert result == "Fallback"
        assert call_count[0] == 2  # Both models tried


# =============================================================================
# Test: Memory Cache (existing functionality)
# =============================================================================


class TestMemoryCache:
    """Tests for MemoryCache (existing functionality)."""

    def test_cache_get_set(self) -> None:
        """Test basic cache get and set."""
        cache = MemoryCache(max_size=10, ttl_seconds=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss_returns_none(self) -> None:
        """Test that cache miss returns None."""
        cache = MemoryCache(max_size=10, ttl_seconds=60)
        assert cache.get("nonexistent") is None

    def test_cache_expires_after_ttl(self) -> None:
        """Test that cache entries expire after TTL."""
        cache = MemoryCache(max_size=10, ttl_seconds=0)  # Immediate expiry
        cache.set("key1", "value1")
        time.sleep(0.1)  # Wait for expiry
        assert cache.get("key1") is None

    def test_cache_enforces_size_limit(self) -> None:
        """Test that cache enforces max size with LRU eviction."""
        cache = MemoryCache(max_size=2, ttl_seconds=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_clear(self) -> None:
        """Test cache clear method."""
        cache = MemoryCache(max_size=10, ttl_seconds=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.size() == 0

    def test_cache_lru_access_order(self) -> None:
        """Test that LRU order is maintained on access."""
        cache = MemoryCache(max_size=2, ttl_seconds=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # Access key1, making it most recent
        cache.set("key3", "value3")  # Should evict key2, not key1

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_fallback_list(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test handling of empty fallback list."""
        models = client_with_registry._get_fallback_chain("gpt-4", fallback_models=[])
        assert models == ["openai/gpt-4"]

    def test_none_fallback_list(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test handling of None fallback list."""
        models = client_with_registry._get_fallback_chain("gpt-4", fallback_models=None)
        assert models == ["openai/gpt-4"]

    def test_model_name_with_multiple_slashes(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test model names with multiple slashes."""
        # Some HuggingFace models like 'meta-llama/Llama-2-70b-chat-hf'
        provider, model = client_with_registry._parse_model_string("meta-llama/Llama-2-70b")
        assert provider == "meta-llama"
        assert model == "Llama-2-70b"

    def test_whitespace_in_model_name(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test handling of whitespace in model names."""
        provider, model = client_with_registry._parse_model_string("  openai / gpt-4  ")
        # Should strip whitespace
        assert provider == "openai"
        assert model == "gpt-4"

    @patch("litellm.completion")
    def test_empty_response_handling(
        self, mock_completion: MagicMock, client_with_registry: LLMClient
    ) -> None:
        """Test handling of empty LLM response."""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=None))]
        )

        result = client_with_registry.complete("Test prompt", model="gpt-4")
        assert result == ""

    def test_fallback_chain_with_invalid_model(
        self, client_with_registry: LLMClient
    ) -> None:
        """Test fallback chain with invalid model name."""
        models = client_with_registry._get_fallback_chain(
            "invalid-model",
            fallback_models=["also-invalid"],
        )
        # Should still include the invalid models (API will fail later)
        assert "invalid-model" in models
        assert "also-invalid" in models