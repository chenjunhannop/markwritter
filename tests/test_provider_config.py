"""Tests for Provider Configuration models (Phase 1)."""

import os
from typing import Optional

import pytest
from pydantic import ValidationError

from markwritter.models import (
    LLMConfig,
    ModelCapability,
    ModelDefinition,
    ProviderConfig,
)


class TestModelCapability:
    """Tests for ModelCapability model."""

    def test_model_capability_defaults(self) -> None:
        """Test ModelCapability has correct default values."""
        capability = ModelCapability()
        assert capability.vision is False
        assert capability.tools is False
        assert capability.streaming is False

    def test_model_capability_custom_values(self) -> None:
        """Test ModelCapability with custom values."""
        capability = ModelCapability(vision=True, tools=True, streaming=True)
        assert capability.vision is True
        assert capability.tools is True
        assert capability.streaming is True

    def test_model_capability_partial_values(self) -> None:
        """Test ModelCapability with partial values."""
        capability = ModelCapability(vision=True)
        assert capability.vision is True
        assert capability.tools is False
        assert capability.streaming is False

    def test_model_capability_invalid_types(self) -> None:
        """Test ModelCapability coerces truthy values."""
        # Pydantic coerces "yes" to True (truthy string)
        capability = ModelCapability(vision="yes")  # type: ignore
        assert capability.vision is True
        # Test with invalid type that cannot be coerced
        with pytest.raises(ValidationError):
            ModelCapability(vision=["invalid"])  # type: ignore


class TestModelDefinition:
    """Tests for ModelDefinition model."""

    def test_model_definition_minimal(self) -> None:
        """Test ModelDefinition with only required fields."""
        model = ModelDefinition(id="gpt-4")
        assert model.id == "gpt-4"
        assert model.name is None
        assert model.capabilities.vision is False
        assert model.context_window == 4096
        assert model.max_tokens == 4096

    def test_model_definition_full(self) -> None:
        """Test ModelDefinition with all fields."""
        model = ModelDefinition(
            id="gpt-4-vision",
            name="GPT-4 Vision",
            capabilities=ModelCapability(vision=True, tools=True),
            context_window=128000,
            max_tokens=4096,
        )
        assert model.id == "gpt-4-vision"
        assert model.name == "GPT-4 Vision"
        assert model.capabilities.vision is True
        assert model.capabilities.tools is True
        assert model.context_window == 128000
        assert model.max_tokens == 4096

    def test_model_definition_custom_defaults(self) -> None:
        """Test ModelDefinition with custom context and token values."""
        model = ModelDefinition(
            id="claude-3-opus",
            context_window=200000,
            max_tokens=4096,
        )
        assert model.context_window == 200000
        assert model.max_tokens == 4096

    def test_model_definition_missing_id(self) -> None:
        """Test ModelDefinition requires id field."""
        with pytest.raises(ValidationError):
            ModelDefinition()  # type: ignore

    def test_model_capability_nested_default(self) -> None:
        """Test ModelDefinition creates default ModelCapability."""
        model = ModelDefinition(id="test-model")
        assert isinstance(model.capabilities, ModelCapability)


class TestProviderConfig:
    """Tests for ProviderConfig model."""

    def test_provider_config_minimal(self) -> None:
        """Test ProviderConfig with minimal required fields."""
        provider = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
        )
        assert provider.name == "openai"
        assert provider.provider_type == "openai"
        assert provider.api_key_env == "OPENAI_API_KEY"
        assert provider.base_url is None
        assert provider.models == []
        assert provider.is_default is False

    def test_provider_config_full(self) -> None:
        """Test ProviderConfig with all fields."""
        models = [
            ModelDefinition(id="gpt-4", name="GPT-4"),
            ModelDefinition(id="gpt-3.5-turbo", name="GPT-3.5 Turbo"),
        ]
        provider = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
            base_url="https://api.openai.com/v1",
            models=models,
            is_default=True,
        )
        assert provider.name == "openai"
        assert provider.provider_type == "openai"
        assert provider.api_key_env == "OPENAI_API_KEY"
        assert provider.base_url == "https://api.openai.com/v1"
        assert len(provider.models) == 2
        assert provider.models[0].id == "gpt-4"
        assert provider.is_default is True

    def test_provider_config_openai_compatible(self) -> None:
        """Test ProviderConfig for OpenAI-compatible providers."""
        provider = ProviderConfig(
            name="ollama",
            provider_type="openai-compatible",
            api_key_env="OLLAMA_API_KEY",
            base_url="http://localhost:11434/v1",
            models=[
                ModelDefinition(id="llama2", name="Llama 2"),
            ],
        )
        assert provider.provider_type == "openai-compatible"
        assert provider.base_url == "http://localhost:11434/v1"

    def test_provider_config_invalid_type(self) -> None:
        """Test ProviderConfig rejects invalid provider_type."""
        with pytest.raises(ValidationError):
            ProviderConfig(
                name="test",
                provider_type="invalid",  # type: ignore
                api_key_env="TEST_KEY",
            )

    def test_provider_config_missing_required(self) -> None:
        """Test ProviderConfig requires name, provider_type, and api_key_env."""
        with pytest.raises(ValidationError):
            ProviderConfig(name="test")  # type: ignore

        with pytest.raises(ValidationError):
            ProviderConfig(name="test", provider_type="openai")  # type: ignore

    def test_provider_config_model_ids_extraction(self) -> None:
        """Test extracting model IDs from provider."""
        provider = ProviderConfig(
            name="anthropic",
            provider_type="anthropic",
            api_key_env="ANTHROPIC_API_KEY",
            models=[
                ModelDefinition(id="claude-3-opus"),
                ModelDefinition(id="claude-3-sonnet"),
            ],
        )
        model_ids = [m.id for m in provider.models]
        assert model_ids == ["claude-3-opus", "claude-3-sonnet"]


class TestLLMConfigExtended:
    """Tests for extended LLMConfig with providers support."""

    def test_llm_config_defaults(self) -> None:
        """Test LLMConfig maintains backward compatibility."""
        config = LLMConfig()
        assert config.default_model == "qwen/qwen3.5-plus"
        assert config.timeout == 30
        assert config.max_retries == 2
        assert config.temperature == 0.1

    def test_llm_config_with_providers(self) -> None:
        """Test LLMConfig with providers list."""
        providers = [
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                is_default=True,
            ),
            ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
            ),
        ]
        config = LLMConfig(providers=providers)
        assert len(config.providers) == 2
        assert config.providers[0].is_default is True

    def test_llm_config_with_fallback_chain(self) -> None:
        """Test LLMConfig with fallback_chain."""
        config = LLMConfig(
            default_model="gpt-4",
            fallback_chain=["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"],
        )
        assert config.fallback_chain == ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"]

    def test_llm_config_fallback_chain_default_empty(self) -> None:
        """Test LLMConfig fallback_chain defaults to empty."""
        config = LLMConfig()
        assert config.fallback_chain == []

    def test_llm_config_providers_default_empty(self) -> None:
        """Test LLMConfig providers defaults to empty."""
        config = LLMConfig()
        assert config.providers == []

    def test_llm_config_full_configuration(self) -> None:
        """Test LLMConfig with complete configuration."""
        providers = [
            ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key_env="OPENAI_API_KEY",
                models=[
                    ModelDefinition(
                        id="gpt-4",
                        capabilities=ModelCapability(vision=True, tools=True),
                    )
                ],
                is_default=True,
            ),
        ]
        config = LLMConfig(
            default_model="gpt-4",
            timeout=60,
            max_retries=3,
            temperature=0.7,
            providers=providers,
            fallback_chain=["gpt-4", "gpt-3.5-turbo"],
        )
        assert config.default_model == "gpt-4"
        assert config.timeout == 60
        assert config.max_retries == 3
        assert config.temperature == 0.7
        assert len(config.providers) == 1
        assert config.providers[0].models[0].capabilities.vision is True
        assert config.fallback_chain == ["gpt-4", "gpt-3.5-turbo"]


class TestProviderConfigIntegration:
    """Integration tests for Provider configuration."""

    def test_multiple_providers_with_models(self) -> None:
        """Test multiple providers each with multiple models."""
        config = LLMConfig(
            providers=[
                ProviderConfig(
                    name="openai",
                    provider_type="openai",
                    api_key_env="OPENAI_API_KEY",
                    models=[
                        ModelDefinition(
                            id="gpt-4-vision",
                            capabilities=ModelCapability(vision=True, tools=True),
                        ),
                        ModelDefinition(
                            id="gpt-3.5-turbo",
                            capabilities=ModelCapability(streaming=True),
                        ),
                    ],
                    is_default=True,
                ),
                ProviderConfig(
                    name="anthropic",
                    provider_type="anthropic",
                    api_key_env="ANTHROPIC_API_KEY",
                    models=[
                        ModelDefinition(
                            id="claude-3-opus",
                            capabilities=ModelCapability(
                                vision=True, tools=True, streaming=True
                            ),
                        ),
                    ],
                ),
            ]
        )
        assert len(config.providers) == 2
        assert len(config.providers[0].models) == 2
        assert len(config.providers[1].models) == 1

    def test_provider_config_serialization(self) -> None:
        """Test ProviderConfig serialization to dict."""
        provider = ProviderConfig(
            name="openai",
            provider_type="openai",
            api_key_env="OPENAI_API_KEY",
            models=[ModelDefinition(id="gpt-4")],
        )
        data = provider.model_dump()
        assert data["name"] == "openai"
        assert data["provider_type"] == "openai"
        assert len(data["models"]) == 1

    def test_llm_config_serialization(self) -> None:
        """Test LLMConfig serialization includes providers."""
        config = LLMConfig(
            default_model="gpt-4",
            providers=[
                ProviderConfig(
                    name="openai",
                    provider_type="openai",
                    api_key_env="OPENAI_API_KEY",
                )
            ],
            fallback_chain=["gpt-4"],
        )
        data = config.model_dump()
        assert "providers" in data
        assert "fallback_chain" in data
        assert len(data["providers"]) == 1
        assert data["fallback_chain"] == ["gpt-4"]


class TestModelCapabilityEdgeCases:
    """Edge case tests for ModelCapability."""

    def test_all_false(self) -> None:
        """Test ModelCapability with all capabilities disabled."""
        cap = ModelCapability(vision=False, tools=False, streaming=False)
        assert not any([cap.vision, cap.tools, cap.streaming])

    def test_all_true(self) -> None:
        """Test ModelCapability with all capabilities enabled."""
        cap = ModelCapability(vision=True, tools=True, streaming=True)
        assert all([cap.vision, cap.tools, cap.streaming])

    def test_from_dict(self) -> None:
        """Test ModelCapability creation from dict."""
        cap = ModelCapability(**{"vision": True, "tools": False})
        assert cap.vision is True
        assert cap.tools is False


class TestModelDefinitionEdgeCases:
    """Edge case tests for ModelDefinition."""

    def test_zero_context_window(self) -> None:
        """Test ModelDefinition with zero context window."""
        model = ModelDefinition(id="test", context_window=0)
        assert model.context_window == 0

    def test_large_context_window(self) -> None:
        """Test ModelDefinition with very large context window."""
        model = ModelDefinition(id="test", context_window=1_000_000)
        assert model.context_window == 1_000_000

    def test_special_characters_in_id(self) -> None:
        """Test ModelDefinition with special characters in ID."""
        model = ModelDefinition(id="model-name_v2.0")
        assert model.id == "model-name_v2.0"

    def test_unicode_name(self) -> None:
        """Test ModelDefinition with unicode name."""
        model = ModelDefinition(id="test", name="测试模型")
        assert model.name == "测试模型"


class TestProviderConfigEdgeCases:
    """Edge case tests for ProviderConfig."""

    def test_empty_models_list(self) -> None:
        """Test ProviderConfig with explicitly empty models list."""
        provider = ProviderConfig(
            name="test",
            provider_type="openai",
            api_key_env="TEST_KEY",
            models=[],
        )
        assert provider.models == []

    def test_many_models(self) -> None:
        """Test ProviderConfig with many models."""
        models = [ModelDefinition(id=f"model-{i}") for i in range(100)]
        provider = ProviderConfig(
            name="test",
            provider_type="openai",
            api_key_env="TEST_KEY",
            models=models,
        )
        assert len(provider.models) == 100

    def test_base_url_trailing_slash(self) -> None:
        """Test ProviderConfig with trailing slash in base_url."""
        provider = ProviderConfig(
            name="test",
            provider_type="openai-compatible",
            api_key_env="TEST_KEY",
            base_url="https://api.example.com/v1/",
        )
        assert provider.base_url == "https://api.example.com/v1/"

    def test_all_provider_types(self) -> None:
        """Test all valid provider types."""
        valid_types = ["openai", "anthropic", "google", "openai-compatible"]
        for ptype in valid_types:
            provider = ProviderConfig(
                name=f"test-{ptype}",
                provider_type=ptype,  # type: ignore
                api_key_env="TEST_KEY",
            )
            assert provider.provider_type == ptype


class TestLLMConfigBackwardCompatibility:
    """Tests ensuring backward compatibility with existing LLMConfig."""

    def test_existing_code_still_works(self) -> None:
        """Test that existing code using LLMConfig still works."""
        # This simulates existing code that doesn't use providers
        config = LLMConfig(
            default_model="custom-model",
            timeout=60,
            temperature=0.5,
        )
        assert config.default_model == "custom-model"
        assert config.timeout == 60
        assert config.temperature == 0.5

    def test_default_values_unchanged(self) -> None:
        """Test that default values remain unchanged."""
        config = LLMConfig()
        assert config.default_model == "qwen/qwen3.5-plus"
        assert config.timeout == 30
        assert config.max_retries == 2
        assert config.temperature == 0.1