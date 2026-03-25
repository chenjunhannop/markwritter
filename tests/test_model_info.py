"""Tests for ModelInfo wrapper class."""

import pytest

from markwritter.models import ModelCapability, ModelDefinition, ProviderConfig
from markwritter.provider_registry import ModelInfo, ProviderRegistry


class TestModelInfoCreation:
    """Tests for ModelInfo creation."""

    def test_create_model_info(self) -> None:
        """ModelInfo can be created with provider name and model definition."""
        model = ModelDefinition(id="gpt-4", capabilities=ModelCapability(vision=True))
        info = ModelInfo(provider="openai", model=model)

        assert info.provider == "openai"
        assert info.model_id == "gpt-4"
        assert info.capabilities == ["vision"]

    def test_full_name_format(self) -> None:
        """ModelInfo.full_name returns provider/model format."""
        model = ModelDefinition(id="gpt-4")
        info = ModelInfo(provider="openai", model=model)

        assert info.full_name == "openai/gpt-4"

    def test_full_name_with_complex_model_id(self) -> None:
        """ModelInfo.full_name handles complex model IDs."""
        model = ModelDefinition(id="claude-3-5-sonnet-20241022")
        info = ModelInfo(provider="anthropic", model=model)

        assert info.full_name == "anthropic/claude-3-5-sonnet-20241022"

    def test_capabilities_list(self) -> None:
        """ModelInfo.capabilities returns list of enabled capabilities."""
        model = ModelDefinition(
            id="gpt-4o", capabilities=ModelCapability(vision=True, tools=True, streaming=True)
        )
        info = ModelInfo(provider="openai", model=model)

        assert set(info.capabilities) == {"vision", "tools", "streaming"}

    def test_capabilities_empty(self) -> None:
        """ModelInfo.capabilities returns empty list when no capabilities."""
        model = ModelDefinition(id="basic-model")
        info = ModelInfo(provider="test", model=model)

        assert info.capabilities == []


class TestModelInfoProperties:
    """Tests for ModelInfo properties."""

    def test_context_window(self) -> None:
        """ModelInfo exposes context_window from model."""
        model = ModelDefinition(id="gpt-4", context_window=128000)
        info = ModelInfo(provider="openai", model=model)

        assert info.context_window == 128000

    def test_max_tokens(self) -> None:
        """ModelInfo exposes max_tokens from model."""
        model = ModelDefinition(id="gpt-4", max_tokens=4096)
        info = ModelInfo(provider="openai", model=model)

        assert info.max_tokens == 4096

    def test_name_fallback_to_id(self) -> None:
        """ModelInfo.name falls back to model.id if name not set."""
        model = ModelDefinition(id="gpt-4")
        info = ModelInfo(provider="openai", model=model)

        assert info.name == "gpt-4"

    def test_name_uses_model_name(self) -> None:
        """ModelInfo.name uses model.name if set."""
        model = ModelDefinition(id="gpt-4", name="GPT-4")
        info = ModelInfo(provider="openai", model=model)

        assert info.name == "GPT-4"


class TestProviderRegistryGetModelInfo:
    """Tests for ProviderRegistry.get_model_info method."""

    @pytest.fixture
    def registry(self) -> ProviderRegistry:
        """Create a registry with test providers."""
        config = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
            models=[
                ModelDefinition(id="gpt-4o", capabilities=ModelCapability(vision=True)),
                ModelDefinition(id="gpt-4o-mini"),
            ],
            is_default=True,
        )
        registry = ProviderRegistry()
        registry.add_provider(config)
        return registry

    def test_get_model_info_by_full_name(self, registry: ProviderRegistry) -> None:
        """get_model_info returns ModelInfo for full name."""
        info = registry.get_model_info("openai/gpt-4o")

        assert info is not None
        assert info.provider == "openai"
        assert info.model_id == "gpt-4o"
        assert info.full_name == "openai/gpt-4o"

    def test_get_model_info_by_short_name(self, registry: ProviderRegistry) -> None:
        """get_model_info returns ModelInfo for short name."""
        info = registry.get_model_info("gpt-4o")

        assert info is not None
        assert info.provider == "openai"
        assert info.model_id == "gpt-4o"

    def test_get_model_info_not_found(self, registry: ProviderRegistry) -> None:
        """get_model_info returns None for unknown model."""
        info = registry.get_model_info("unknown-model")

        assert info is None

    def test_get_model_info_with_capabilities(self, registry: ProviderRegistry) -> None:
        """get_model_info returns ModelInfo with correct capabilities."""
        info = registry.get_model_info("gpt-4o")

        assert info is not None
        assert "vision" in info.capabilities


class TestProviderRegistryGetModelsByCapability:
    """Tests for ProviderRegistry.get_models_by_capability method."""

    @pytest.fixture
    def registry(self) -> ProviderRegistry:
        """Create a registry with models having different capabilities."""
        registry = ProviderRegistry()

        # OpenAI provider
        openai = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
            models=[
                ModelDefinition(id="gpt-4o", capabilities=ModelCapability(vision=True, tools=True)),
                ModelDefinition(id="gpt-4o-mini", capabilities=ModelCapability(tools=True)),
            ],
            is_default=True,
        )
        registry.add_provider(openai)

        # Anthropic provider
        anthropic = ProviderConfig(
            name="anthropic",
            provider_type="anthropic",
            api_key_env="ANTHROPIC_API_KEY",
            models=[
                ModelDefinition(
                    id="claude-3-5-sonnet", capabilities=ModelCapability(vision=True, tools=True)
                ),
            ],
        )
        registry.add_provider(anthropic)

        return registry

    def test_get_models_by_capability_vision(self, registry: ProviderRegistry) -> None:
        """get_models_by_capability returns models with vision capability."""
        models = registry.get_models_by_capability("vision")

        model_ids = [m.model_id for m in models]
        assert "gpt-4o" in model_ids
        assert "claude-3-5-sonnet" in model_ids
        assert "gpt-4o-mini" not in model_ids

    def test_get_models_by_capability_tools(self, registry: ProviderRegistry) -> None:
        """get_models_by_capability returns models with tools capability."""
        models = registry.get_models_by_capability("tools")

        model_ids = [m.model_id for m in models]
        assert "gpt-4o" in model_ids
        assert "gpt-4o-mini" in model_ids
        assert "claude-3-5-sonnet" in model_ids

    def test_get_models_by_capability_streaming(self, registry: ProviderRegistry) -> None:
        """get_models_by_capability returns empty list for capability with no models."""
        models = registry.get_models_by_capability("streaming")

        assert models == []

    def test_models_have_full_name(self, registry: ProviderRegistry) -> None:
        """All returned models have full_name property."""
        models = registry.get_models_by_capability("vision")

        for model in models:
            assert model.full_name is not None
            assert "/" in model.full_name


class TestModelInfoProtocol:
    """Tests ensuring ModelInfo matches the Protocol in llm_client.py."""

    def test_matches_protocol_provider(self) -> None:
        """ModelInfo has provider property matching protocol."""
        model = ModelDefinition(id="test")
        info = ModelInfo(provider="test-provider", model=model)

        assert hasattr(info, "provider")
        assert isinstance(info.provider, str)

    def test_matches_protocol_model_id(self) -> None:
        """ModelInfo has model_id property matching protocol."""
        model = ModelDefinition(id="test-model")
        info = ModelInfo(provider="test", model=model)

        assert hasattr(info, "model_id")
        assert isinstance(info.model_id, str)

    def test_matches_protocol_capabilities(self) -> None:
        """ModelInfo has capabilities property matching protocol."""
        model = ModelDefinition(id="test")
        info = ModelInfo(provider="test", model=model)

        assert hasattr(info, "capabilities")
        assert isinstance(info.capabilities, list)

    def test_matches_protocol_full_name(self) -> None:
        """ModelInfo has full_name property matching protocol."""
        model = ModelDefinition(id="test")
        info = ModelInfo(provider="test", model=model)

        assert hasattr(info, "full_name")
        assert isinstance(info.full_name, str)
        assert info.full_name == "test/test"
