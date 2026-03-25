"""Tests for Provider Registry (Phase 2)."""

import os
from unittest.mock import patch

import pytest

from markwritter.models import (
    LLMConfig,
    ModelCapability,
    ModelDefinition,
    ProviderConfig,
)
from markwritter.provider_registry import ProviderRegistry


class TestProviderRegistryInit:
    """Tests for ProviderRegistry initialization."""

    def test_init_empty(self) -> None:
        """Test ProviderRegistry initialization with no providers."""
        registry = ProviderRegistry()
        assert registry.list_providers() == []
        assert registry.list_models() == []

    def test_init_with_config(self) -> None:
        """Test ProviderRegistry initialization with LLMConfig."""
        config = LLMConfig(
            providers=[
                ProviderConfig(
                    name="openai",
                    provider_type="openai",
                    api_key_env="OPENAI_API_KEY",
                    models=[ModelDefinition(id="gpt-4")],
                )
            ]
        )
        registry = ProviderRegistry(config)
        assert len(registry.list_providers()) == 1

    def test_init_with_none_config(self) -> None:
        """Test ProviderRegistry initialization with None config."""
        registry = ProviderRegistry(None)
        assert registry.list_providers() == []


class TestProviderRegistryAddProvider:
    """Tests for adding providers to registry."""

    def test_add_single_provider(self) -> None:
        """Test adding a single provider."""
        registry = ProviderRegistry()
        provider = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
        )
        registry.add_provider(provider)
        assert len(registry.list_providers()) == 1

    def test_add_multiple_providers(self) -> None:
        """Test adding multiple providers."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
            )
        )
        registry.add_provider(
            ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
            )
        )
        assert len(registry.list_providers()) == 2

    def test_add_provider_with_models(self) -> None:
        """Test adding provider with models."""
        registry = ProviderRegistry()
        provider = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
            models=[
                ModelDefinition(id="gpt-4"),
                ModelDefinition(id="gpt-3.5-turbo"),
            ],
        )
        registry.add_provider(provider)
        assert len(registry.list_models()) == 2


class TestProviderRegistryGetProvider:
    """Tests for retrieving providers."""

    def test_get_provider_by_name(self) -> None:
        """Test getting provider by name."""
        registry = ProviderRegistry()
        provider = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
        )
        registry.add_provider(provider)
        retrieved = registry.get_provider("openai")
        assert retrieved is not None
        assert retrieved.name == "openai"

    def test_get_provider_not_found(self) -> None:
        """Test getting non-existent provider."""
        registry = ProviderRegistry()
        assert registry.get_provider("nonexistent") is None

    def test_get_default_provider(self) -> None:
        """Test getting the default provider."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
            )
        )
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                is_default=True,
            )
        )
        default = registry.get_default_provider()
        assert default is not None
        assert default.name == "openai"

    def test_get_default_provider_none(self) -> None:
        """Test getting default when none is set."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
            )
        )
        assert registry.get_default_provider() is None


class TestProviderRegistryModelLookup:
    """Tests for model lookup."""

    def test_get_model_by_id(self) -> None:
        """Test getting model by ID."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4", name="GPT-4")],
            )
        )
        model = registry.get_model("gpt-4")
        assert model is not None
        assert model.id == "gpt-4"
        assert model.name == "GPT-4"

    def test_get_model_not_found(self) -> None:
        """Test getting non-existent model."""
        registry = ProviderRegistry()
        assert registry.get_model("nonexistent") is None

    def test_get_model_with_provider_name(self) -> None:
        """Test getting model with provider/model format."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4")],
            )
        )
        registry.add_provider(
            ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                models=[ModelDefinition(id="claude-3")],
            )
        )
        model = registry.get_model("openai/gpt-4")
        assert model is not None
        assert model.id == "gpt-4"

    def test_get_model_with_wrong_provider(self) -> None:
        """Test getting model with wrong provider prefix."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4")],
            )
        )
        # Model exists but with different provider prefix
        model = registry.get_model("anthropic/gpt-4")
        assert model is None

    def test_list_models(self) -> None:
        """Test listing all models."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[
                    ModelDefinition(id="gpt-4"),
                    ModelDefinition(id="gpt-3.5-turbo"),
                ],
            )
        )
        models = registry.list_models()
        assert len(models) == 2
        model_ids = [m.id for m in models]
        assert "gpt-4" in model_ids
        assert "gpt-3.5-turbo" in model_ids

    def test_list_models_by_provider(self) -> None:
        """Test listing models by provider."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4")],
            )
        )
        registry.add_provider(
            ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                models=[ModelDefinition(id="claude-3")],
            )
        )
        openai_models = registry.list_models(provider_name="openai")
        assert len(openai_models) == 1
        assert openai_models[0].id == "gpt-4"

    def test_list_models_nonexistent_provider(self) -> None:
        """Test listing models for non-existent provider."""
        registry = ProviderRegistry()
        models = registry.list_models(provider_name="nonexistent")
        assert models == []

    def test_get_model_provider(self) -> None:
        """Test getting the provider for a model."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4")],
            )
        )
        provider = registry.get_model_provider("gpt-4")
        assert provider is not None
        assert provider.name == "openai"

    def test_get_model_provider_not_found(self) -> None:
        """Test getting provider for non-existent model."""
        registry = ProviderRegistry()
        assert registry.get_model_provider("nonexistent") is None


class TestProviderRegistryAPIKeyResolution:
    """Tests for API key resolution."""

    def test_get_api_key_from_env(self) -> None:
        """Test getting API key from environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
            registry = ProviderRegistry()
            registry.add_provider(
                ProviderConfig(
                    name="openai",
                    provider_type="openai",
                    api_key_env="OPENAI_API_KEY",
                )
            )
            api_key = registry.get_api_key("openai")
            assert api_key == "test-key-123"

    def test_get_api_key_missing_env(self) -> None:
        """Test getting API key when env var is not set."""
        # Ensure the env var is not set
        with patch.dict(os.environ, {}, clear=True):
            registry = ProviderRegistry()
            registry.add_provider(
                ProviderConfig(
                    name="openai",
                    provider_type="openai",
                    api_key_env="MISSING_API_KEY",
                )
            )
            api_key = registry.get_api_key("openai")
            assert api_key is None

    def test_get_api_key_nonexistent_provider(self) -> None:
        """Test getting API key for non-existent provider."""
        registry = ProviderRegistry()
        assert registry.get_api_key("nonexistent") is None

    def test_get_api_key_by_model(self) -> None:
        """Test getting API key by model ID."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "anthropic-key"}):
            registry = ProviderRegistry()
            registry.add_provider(
                ProviderConfig(
                    name="anthropic",
                    provider_type="anthropic",
                    api_key_env="ANTHROPIC_API_KEY",
                    models=[ModelDefinition(id="claude-3")],
                )
            )
            api_key = registry.get_api_key_for_model("claude-3")
            assert api_key == "anthropic-key"

    def test_get_api_key_for_model_not_found(self) -> None:
        """Test getting API key for non-existent model."""
        registry = ProviderRegistry()
        assert registry.get_api_key_for_model("nonexistent") is None


class TestProviderRegistryModelCapabilities:
    """Tests for model capability queries."""

    def test_get_model_capabilities(self) -> None:
        """Test getting model capabilities."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[
                    ModelDefinition(
                        id="gpt-4-vision",
                        capabilities=ModelCapability(vision=True, tools=True),
                    )
                ],
            )
        )
        capabilities = registry.get_model_capabilities("gpt-4-vision")
        assert capabilities is not None
        assert capabilities.vision is True
        assert capabilities.tools is True
        assert capabilities.streaming is False

    def test_get_model_capabilities_not_found(self) -> None:
        """Test getting capabilities for non-existent model."""
        registry = ProviderRegistry()
        assert registry.get_model_capabilities("nonexistent") is None

    def test_get_model_capabilities_default(self) -> None:
        """Test getting capabilities for model with default capabilities."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-3.5-turbo")],
            )
        )
        capabilities = registry.get_model_capabilities("gpt-3.5-turbo")
        assert capabilities is not None
        assert capabilities.vision is False
        assert capabilities.tools is False

    def test_has_capability(self) -> None:
        """Test checking if model has specific capability."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[
                    ModelDefinition(
                        id="gpt-4-vision",
                        capabilities=ModelCapability(vision=True),
                    )
                ],
            )
        )
        assert registry.has_capability("gpt-4-vision", "vision") is True
        assert registry.has_capability("gpt-4-vision", "tools") is False

    def test_has_capability_nonexistent_model(self) -> None:
        """Test capability check for non-existent model."""
        registry = ProviderRegistry()
        assert registry.has_capability("nonexistent", "vision") is False

    def test_has_capability_invalid_capability(self) -> None:
        """Test capability check with invalid capability name."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4")],
            )
        )
        with pytest.raises(ValueError):
            registry.has_capability("gpt-4", "invalid_capability")


class TestProviderRegistryModelIndex:
    """Tests for model index functionality."""

    def test_model_index_built_on_init(self) -> None:
        """Test that model index is built during initialization."""
        config = LLMConfig(
            providers=[
                ProviderConfig(
                    name="openai",
                    provider_type="openai",
                    api_key_env="OPENAI_API_KEY",
                    models=[
                        ModelDefinition(id="gpt-4"),
                        ModelDefinition(id="gpt-3.5-turbo"),
                    ],
                ),
                ProviderConfig(
                    name="anthropic",
                    provider_type="anthropic",
                    api_key_env="ANTHROPIC_API_KEY",
                    models=[ModelDefinition(id="claude-3")],
                ),
            ]
        )
        registry = ProviderRegistry(config)
        # All models should be indexed
        assert registry.get_model("gpt-4") is not None
        assert registry.get_model("gpt-3.5-turbo") is not None
        assert registry.get_model("claude-3") is not None

    def test_model_index_updated_on_add(self) -> None:
        """Test that model index is updated when provider is added."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4")],
            )
        )
        # Model should be indexed
        assert registry.get_model("gpt-4") is not None

    def test_duplicate_model_id_across_providers(self) -> None:
        """Test handling duplicate model IDs across providers."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="provider1",
                provider_type="openai-compatible",
                api_key_env="PROVIDER1_KEY",
                models=[ModelDefinition(id="llama2")],
            )
        )
        registry.add_provider(
            ProviderConfig(
                name="provider2",
                provider_type="openai-compatible",
                api_key_env="PROVIDER2_KEY",
                models=[ModelDefinition(id="llama2")],
            )
        )
        # Should return first provider's model
        model = registry.get_model("llama2")
        assert model is not None
        provider = registry.get_model_provider("llama2")
        assert provider is not None
        # Could be either provider, but should return one
        assert provider.name in ["provider1", "provider2"]

    def test_resolve_model_ambiguous_with_prefix(self) -> None:
        """Test resolving ambiguous model ID with provider prefix."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="provider1",
                provider_type="openai-compatible",
                api_key_env="PROVIDER1_KEY",
                models=[ModelDefinition(id="llama2", name="Llama 2 - P1")],
            )
        )
        registry.add_provider(
            ProviderConfig(
                name="provider2",
                provider_type="openai-compatible",
                api_key_env="PROVIDER2_KEY",
                models=[ModelDefinition(id="llama2", name="Llama 2 - P2")],
            )
        )
        # Should resolve to specific provider with prefix
        model = registry.get_model("provider2/llama2")
        assert model is not None
        assert model.name == "Llama 2 - P2"


class TestProviderRegistryGetProviderByModel:
    """Tests for finding provider by model."""

    def test_get_provider_for_model(self) -> None:
        """Test getting provider that owns a model."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4")],
            )
        )
        provider = registry.get_provider_for_model("gpt-4")
        assert provider is not None
        assert provider.name == "openai"

    def test_get_provider_for_model_not_found(self) -> None:
        """Test getting provider for non-existent model."""
        registry = ProviderRegistry()
        assert registry.get_provider_for_model("nonexistent") is None


class TestProviderRegistryValidation:
    """Tests for registry validation."""

    def test_validate_provider_config(self) -> None:
        """Test validating provider configuration."""
        registry = ProviderRegistry()
        provider = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
            models=[ModelDefinition(id="gpt-4")],
        )
        # Should not raise
        registry.add_provider(provider)
        assert len(registry.list_providers()) == 1


class TestProviderRegistryListMethods:
    """Tests for list methods."""

    def test_list_provider_names(self) -> None:
        """Test listing provider names."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
            )
        )
        registry.add_provider(
            ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
            )
        )
        names = registry.list_provider_names()
        assert "openai" in names
        assert "anthropic" in names

    def test_list_model_ids(self) -> None:
        """Test listing model IDs."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[
                    ModelDefinition(id="gpt-4"),
                    ModelDefinition(id="gpt-3.5-turbo"),
                ],
            )
        )
        model_ids = registry.list_model_ids()
        assert "gpt-4" in model_ids
        assert "gpt-3.5-turbo" in model_ids

    def test_list_model_ids_with_provider(self) -> None:
        """Test listing model IDs with provider prefix."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4")],
            )
        )
        model_ids = registry.list_model_ids(include_provider=True)
        assert "openai/gpt-4" in model_ids


class TestProviderRegistryGetProviderType:
    """Tests for getting provider type."""

    def test_get_provider_type(self) -> None:
        """Test getting provider type by name."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="ollama",
                provider_type="openai-compatible",
                api_key_env="OLLAMA_API_KEY",
            )
        )
        provider_type = registry.get_provider_type("ollama")
        assert provider_type == "openai-compatible"

    def test_get_provider_type_not_found(self) -> None:
        """Test getting provider type for non-existent provider."""
        registry = ProviderRegistry()
        assert registry.get_provider_type("nonexistent") is None

    def test_get_provider_type_for_model(self) -> None:
        """Test getting provider type for a model."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                models=[ModelDefinition(id="claude-3")],
            )
        )
        provider_type = registry.get_provider_type_for_model("claude-3")
        assert provider_type == "anthropic"

    def test_get_provider_type_for_model_not_found(self) -> None:
        """Test getting provider type for non-existent model."""
        registry = ProviderRegistry()
        assert registry.get_provider_type_for_model("nonexistent") is None


class TestProviderRegistryGetBaseURL:
    """Tests for getting base URL."""

    def test_get_base_url(self) -> None:
        """Test getting base URL for provider."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="ollama",
                provider_type="openai-compatible",
                api_key_env="OLLAMA_API_KEY",
                base_url="http://localhost:11434/v1",
            )
        )
        base_url = registry.get_base_url("ollama")
        assert base_url == "http://localhost:11434/v1"

    def test_get_base_url_none(self) -> None:
        """Test getting base URL when not set."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
            )
        )
        assert registry.get_base_url("openai") is None

    def test_get_base_url_not_found(self) -> None:
        """Test getting base URL for non-existent provider."""
        registry = ProviderRegistry()
        assert registry.get_base_url("nonexistent") is None


class TestProviderRegistryEdgeCases:
    """Edge case tests for ProviderRegistry."""

    def test_empty_model_id(self) -> None:
        """Test lookup with empty model ID."""
        registry = ProviderRegistry()
        assert registry.get_model("") is None

    def test_empty_provider_name(self) -> None:
        """Test lookup with empty provider name."""
        registry = ProviderRegistry()
        assert registry.get_provider("") is None

    def test_whitespace_in_names(self) -> None:
        """Test handling whitespace in names."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="  openai  ",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="  gpt-4  ")],
            )
        )
        # Pydantic should handle stripping or we need to handle it
        assert registry.get_provider("  openai  ") is not None

    def test_case_sensitivity(self) -> None:
        """Test case sensitivity in lookups."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="OpenAI",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="GPT-4")],
            )
        )
        # Provider names should be case-sensitive
        assert registry.get_provider("OpenAI") is not None
        assert registry.get_provider("openai") is None

    def test_model_with_slash_in_id(self) -> None:
        """Test model ID containing slash."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[ModelDefinition(id="gpt-4-0613")],
            )
        )
        # Should not be confused with provider/model format
        model = registry.get_model("gpt-4-0613")
        assert model is not None

    def test_very_long_model_id(self) -> None:
        """Test model with very long ID."""
        long_id = "a" * 1000
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="test",
                provider_type="openai",
                api_key_env="TEST_KEY",
                models=[ModelDefinition(id=long_id)],
            )
        )
        model = registry.get_model(long_id)
        assert model is not None
        assert model.id == long_id


class TestProviderRegistryConfigUpdate:
    """Tests for updating registry from config."""

    def test_update_from_config(self) -> None:
        """Test updating registry from LLMConfig."""
        registry = ProviderRegistry()
        config = LLMConfig(
            providers=[
                ProviderConfig(
                    name="openai",
                    provider_type="openai",
                    api_key_env="OPENAI_API_KEY",
                    models=[ModelDefinition(id="gpt-4")],
                )
            ]
        )
        registry.update_from_config(config)
        assert len(registry.list_providers()) == 1
        assert registry.get_model("gpt-4") is not None

    def test_update_from_none_config(self) -> None:
        """Test updating registry with None config."""
        registry = ProviderRegistry()
        registry.update_from_config(None)
        assert len(registry.list_providers()) == 0

    def test_update_replaces_existing(self) -> None:
        """Test that update_from_config replaces existing providers."""
        registry = ProviderRegistry()
        registry.add_provider(
            ProviderConfig(
                name="old",
                provider_type="openai",
                api_key_env="OLD_KEY",
            )
        )
        config = LLMConfig(
            providers=[
                ProviderConfig(
                    name="new",
                    provider_type="anthropic",
                    api_key_env="NEW_KEY",
                )
            ]
        )
        registry.update_from_config(config)
        assert registry.get_provider("old") is None
        assert registry.get_provider("new") is not None
