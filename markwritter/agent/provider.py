"""Provider registry for LLM providers.

ProviderRegistry provides a unified interface for LLM operations.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol


class LLMProviderProtocol(Protocol):
    """Protocol for LLM providers."""

    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send completion request."""
        ...

    def chat_complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send chat completion request."""
        ...


class ProviderRegistry:
    """Registry for LLM providers.

    Provides a unified interface for LLM operations with support
    for multiple providers and models.

    Example:
        >>> from markwritter.llm_client import LLMClient
        >>> client = LLMClient()
        >>> registry = ProviderRegistry(default_provider=client)
        >>> result = registry.complete("Hello, world!", model="gpt-4")
    """

    def __init__(self, default_provider: Optional[LLMProviderProtocol] = None) -> None:
        """Initialize the provider registry.

        Args:
            default_provider: Default LLM provider to use
        """
        self._default_provider = default_provider
        self._providers: dict[str, LLMProviderProtocol] = {}

        if default_provider:
            self._providers["default"] = default_provider

    def register(self, name: str, provider: LLMProviderProtocol) -> None:
        """Register a provider.

        Args:
            name: Provider name
            provider: LLM provider instance
        """
        self._providers[name] = provider

    def get(self, name: str) -> Optional[LLMProviderProtocol]:
        """Get a provider by name.

        Args:
            name: Provider name

        Returns:
            Provider instance or None
        """
        return self._providers.get(name)

    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        provider: Optional[str] = None,
    ) -> str:
        """Send completion request.

        Args:
            prompt: The prompt to send
            model: Model to use
            temperature: Temperature setting
            max_tokens: Maximum tokens to generate
            provider: Provider name (uses default if not specified)

        Returns:
            LLM response text

        Raises:
            ValueError: If no provider is available
        """
        provider_instance = self._get_provider(provider)

        return provider_instance.complete(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def chat_complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        provider: Optional[str] = None,
    ) -> str:
        """Send chat completion request.

        Args:
            messages: List of message dicts
            model: Model to use
            temperature: Temperature setting
            max_tokens: Maximum tokens to generate
            provider: Provider name (uses default if not specified)

        Returns:
            LLM response text

        Raises:
            ValueError: If no provider is available
        """
        provider_instance = self._get_provider(provider)

        return provider_instance.chat_complete(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _get_provider(self, name: Optional[str] = None) -> LLMProviderProtocol:
        """Get provider by name or default.

        Args:
            name: Provider name or None for default

        Returns:
            LLM provider instance

        Raises:
            ValueError: If no provider is available
        """
        if name:
            provider = self._providers.get(name)
            if not provider:
                raise ValueError(f"Provider '{name}' not found")
            return provider

        if self._default_provider:
            return self._default_provider

        provider = self._providers.get("default")
        if not provider:
            raise ValueError("No default provider configured")

        return provider

    def list_providers(self) -> list[str]:
        """List registered provider names.

        Returns:
            List of provider names
        """
        return list(self._providers.keys())