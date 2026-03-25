"""Tests for ProviderRegistry - LLM provider management.

TDD Phase: Additional tests for coverage improvement.
"""

import pytest
from unittest.mock import MagicMock

from markwritter.agent.provider import ProviderRegistry


class TestProviderRegistryCreation:
    """Test ProviderRegistry initialization."""

    def test_create_without_provider(self) -> None:
        """Create ProviderRegistry without default provider."""
        registry = ProviderRegistry()

        assert registry is not None

    def test_create_with_provider(self) -> None:
        """Create ProviderRegistry with default provider."""
        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="result")

        registry = ProviderRegistry(default_provider=mock_provider)

        assert registry._default_provider == mock_provider


class TestProviderRegistryRegister:
    """Test ProviderRegistry.register method."""

    def test_register_provider(self) -> None:
        """Register a provider."""
        registry = ProviderRegistry()
        mock_provider = MagicMock()

        registry.register("custom", mock_provider)

        assert registry.get("custom") == mock_provider

    def test_register_multiple_providers(self) -> None:
        """Register multiple providers."""
        registry = ProviderRegistry()
        mock1 = MagicMock()
        mock2 = MagicMock()

        registry.register("provider1", mock1)
        registry.register("provider2", mock2)

        assert registry.get("provider1") == mock1
        assert registry.get("provider2") == mock2

    def test_register_overwrites(self) -> None:
        """Register should overwrite existing provider."""
        registry = ProviderRegistry()
        mock1 = MagicMock()
        mock2 = MagicMock()

        registry.register("test", mock1)
        registry.register("test", mock2)

        assert registry.get("test") == mock2


class TestProviderRegistryGet:
    """Test ProviderRegistry.get method."""

    def test_get_existing_provider(self) -> None:
        """Get an existing provider."""
        registry = ProviderRegistry()
        mock_provider = MagicMock()

        registry.register("test", mock_provider)
        result = registry.get("test")

        assert result == mock_provider

    def test_get_nonexistent_provider(self) -> None:
        """Get a nonexistent provider returns None."""
        registry = ProviderRegistry()

        result = registry.get("nonexistent")

        assert result is None


class TestProviderRegistryComplete:
    """Test ProviderRegistry.complete method."""

    def test_complete_with_default_provider(self) -> None:
        """Complete using default provider."""
        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="response")

        registry = ProviderRegistry(default_provider=mock_provider)
        result = registry.complete("test prompt")

        assert result == "response"
        mock_provider.complete.assert_called_once()

    def test_complete_with_named_provider(self) -> None:
        """Complete using named provider."""
        mock_default = MagicMock()
        mock_custom = MagicMock()
        mock_custom.complete = MagicMock(return_value="custom response")

        registry = ProviderRegistry(default_provider=mock_default)
        registry.register("custom", mock_custom)

        result = registry.complete("test", provider="custom")

        assert result == "custom response"
        mock_custom.complete.assert_called_once()

    def test_complete_with_model_parameter(self) -> None:
        """Complete with model parameter."""
        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="result")

        registry = ProviderRegistry(default_provider=mock_provider)
        registry.complete("prompt", model="gpt-4")

        mock_provider.complete.assert_called_once()
        call_kwargs = mock_provider.complete.call_args[1]
        assert call_kwargs["model"] == "gpt-4"

    def test_complete_with_temperature(self) -> None:
        """Complete with temperature parameter."""
        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="result")

        registry = ProviderRegistry(default_provider=mock_provider)
        registry.complete("prompt", temperature=0.5)

        mock_provider.complete.assert_called_once()
        call_kwargs = mock_provider.complete.call_args[1]
        assert call_kwargs["temperature"] == 0.5

    def test_complete_with_max_tokens(self) -> None:
        """Complete with max_tokens parameter."""
        mock_provider = MagicMock()
        mock_provider.complete = MagicMock(return_value="result")

        registry = ProviderRegistry(default_provider=mock_provider)
        registry.complete("prompt", max_tokens=100)

        mock_provider.complete.assert_called_once()
        call_kwargs = mock_provider.complete.call_args[1]
        assert call_kwargs["max_tokens"] == 100

    def test_complete_no_provider_raises_error(self) -> None:
        """Complete without provider raises error."""
        registry = ProviderRegistry()

        with pytest.raises(ValueError, match="No default provider"):
            registry.complete("prompt")

    def test_complete_unknown_provider_raises_error(self) -> None:
        """Complete with unknown provider raises error."""
        mock_provider = MagicMock()
        registry = ProviderRegistry(default_provider=mock_provider)

        with pytest.raises(ValueError, match="Provider 'unknown' not found"):
            registry.complete("prompt", provider="unknown")


class TestProviderRegistryChatComplete:
    """Test ProviderRegistry.chat_complete method."""

    def test_chat_complete_with_default_provider(self) -> None:
        """Chat complete using default provider."""
        mock_provider = MagicMock()
        mock_provider.chat_complete = MagicMock(return_value="chat response")

        registry = ProviderRegistry(default_provider=mock_provider)
        messages = [{"role": "user", "content": "Hello"}]

        result = registry.chat_complete(messages)

        assert result == "chat response"
        mock_provider.chat_complete.assert_called_once()

    def test_chat_complete_with_parameters(self) -> None:
        """Chat complete with model, temperature, max_tokens."""
        mock_provider = MagicMock()
        mock_provider.chat_complete = MagicMock(return_value="result")

        registry = ProviderRegistry(default_provider=mock_provider)
        messages = [{"role": "user", "content": "Hello"}]

        registry.chat_complete(
            messages,
            model="claude-3",
            temperature=0.8,
            max_tokens=500,
        )

        call_kwargs = mock_provider.chat_complete.call_args[1]
        assert call_kwargs["model"] == "claude-3"
        assert call_kwargs["temperature"] == 0.8
        assert call_kwargs["max_tokens"] == 500

    def test_chat_complete_no_provider_raises_error(self) -> None:
        """Chat complete without provider raises error."""
        registry = ProviderRegistry()
        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(ValueError, match="No default provider"):
            registry.chat_complete(messages)


class TestProviderRegistryListProviders:
    """Test ProviderRegistry.list_providers method."""

    def test_list_providers_empty(self) -> None:
        """List providers when empty."""
        registry = ProviderRegistry()

        result = registry.list_providers()

        assert result == []

    def test_list_providers_with_default(self) -> None:
        """List providers with default provider."""
        mock_provider = MagicMock()
        registry = ProviderRegistry(default_provider=mock_provider)

        result = registry.list_providers()

        assert "default" in result

    def test_list_providers_with_multiple(self) -> None:
        """List multiple providers."""
        registry = ProviderRegistry()
        registry.register("provider1", MagicMock())
        registry.register("provider2", MagicMock())

        result = registry.list_providers()

        assert len(result) == 2
        assert "provider1" in result
        assert "provider2" in result