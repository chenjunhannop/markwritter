"""Provider Registry for managing LLM providers and models.

Phase 2 implementation: Provider Registry with model index and capability queries.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from markwritter.models import LLMConfig, ModelCapability, ModelDefinition, ProviderConfig


@dataclass
class ModelInfo:
    """Wrapper class providing model information with provider context.

    This class implements the ModelInfo protocol expected by LLMClient,
    providing a full_name property that combines provider and model ID.

    Attributes:
        provider: The provider name (e.g., "openai", "anthropic")
        model: The model definition
    """

    provider: str
    model: ModelDefinition

    @property
    def model_id(self) -> str:
        """Get the model ID."""
        return self.model.id

    @property
    def full_name(self) -> str:
        """Get the full model name in provider/model format."""
        return f"{self.provider}/{self.model.id}"

    @property
    def capabilities(self) -> list[str]:
        """Get list of enabled capabilities."""
        caps = []
        if self.model.capabilities.vision:
            caps.append("vision")
        if self.model.capabilities.tools:
            caps.append("tools")
        if self.model.capabilities.streaming:
            caps.append("streaming")
        return caps

    @property
    def context_window(self) -> int:
        """Get the context window size."""
        return self.model.context_window

    @property
    def max_tokens(self) -> int:
        """Get the max output tokens."""
        return self.model.max_tokens

    @property
    def name(self) -> str:
        """Get the display name, falling back to model ID."""
        return self.model.name or self.model.id


class ProviderRegistry:
    """Registry for managing LLM providers and their models.

    Features:
    - Provider management (add, get, list)
    - Model lookup by ID with optional provider prefix (e.g., "openai/gpt-4")
    - API key resolution from environment variables
    - Model capability queries
    - Default provider handling
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize the registry.

        Args:
            config: Optional LLMConfig to initialize with providers.
        """
        self._providers: dict[str, ProviderConfig] = {}
        self._model_index: dict[str, tuple[ProviderConfig, ModelDefinition]] = {}

        if config is not None:
            self.update_from_config(config)

    def add_provider(self, provider: ProviderConfig) -> None:
        """Add a provider to the registry.

        Args:
            provider: ProviderConfig to add.
        """
        self._providers[provider.name] = provider
        # Index all models from this provider
        for model in provider.models:
            key = f"{provider.name}/{model.id}"
            self._model_index[key] = (provider, model)
            # Also index by model ID alone (for backward compatibility)
            # If there's a conflict, we keep the first one
            if model.id not in self._model_index:
                self._model_index[model.id] = (provider, model)

    def update_from_config(self, config: Optional[LLMConfig]) -> None:
        """Update registry from LLMConfig.

        This replaces all existing providers.

        Args:
            config: LLMConfig with providers to register.
        """
        self._providers.clear()
        self._model_index.clear()

        if config is not None:
            for provider in config.providers:
                self.add_provider(provider)

    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """Get a provider by name.

        Args:
            name: Provider name.

        Returns:
            ProviderConfig if found, None otherwise.
        """
        return self._providers.get(name)

    def get_default_provider(self) -> Optional[ProviderConfig]:
        """Get the default provider.

        Returns:
            ProviderConfig marked as default, or None if not set.
        """
        for provider in self._providers.values():
            if provider.is_default:
                return provider
        return None

    def list_providers(self) -> list[ProviderConfig]:
        """List all registered providers.

        Returns:
            List of all ProviderConfig instances.
        """
        return list(self._providers.values())

    def list_provider_names(self) -> list[str]:
        """List all provider names.

        Returns:
            List of provider names.
        """
        return list(self._providers.keys())

    def get_model(self, model_id: str) -> Optional[ModelDefinition]:
        """Get a model by ID.

        Supports both simple IDs ("gpt-4") and prefixed IDs ("openai/gpt-4").

        Args:
            model_id: Model ID, optionally prefixed with provider name.

        Returns:
            ModelDefinition if found, None otherwise.
        """
        result = self._model_index.get(model_id)
        return result[1] if result else None

    def get_model_provider(self, model_id: str) -> Optional[ProviderConfig]:
        """Get the provider for a model.

        Args:
            model_id: Model ID.

        Returns:
            ProviderConfig if found, None otherwise.
        """
        result = self._model_index.get(model_id)
        return result[0] if result else None

    get_provider_for_model = get_model_provider  # Alias for clarity

    def list_models(self, provider_name: Optional[str] = None) -> list[ModelDefinition]:
        """List all models, optionally filtered by provider.

        Args:
            provider_name: Optional provider name to filter by.

        Returns:
            List of ModelDefinition instances.
        """
        if provider_name is not None:
            provider = self._providers.get(provider_name)
            return list(provider.models) if provider else []

        # Return unique models (by model ID)
        seen_ids: set[str] = set()
        models: list[ModelDefinition] = []
        for key, (provider, model) in self._model_index.items():
            # Only include non-prefixed keys to avoid duplicates
            if "/" not in key:
                if model.id not in seen_ids:
                    seen_ids.add(model.id)
                    models.append(model)
        return models

    def list_model_ids(self, include_provider: bool = False) -> list[str]:
        """List all model IDs.

        Args:
            include_provider: If True, include provider prefix.

        Returns:
            List of model IDs.
        """
        if include_provider:
            return [key for key in self._model_index.keys() if "/" in key]
        return [model.id for _, model in self._model_index.values()]

    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key for a provider from environment variable.

        Args:
            provider_name: Provider name.

        Returns:
            API key if found in environment, None otherwise.
        """
        provider = self._providers.get(provider_name)
        if provider is None:
            return None

        return os.environ.get(provider.api_key_env)

    def get_api_key_for_model(self, model_id: str) -> Optional[str]:
        """Get API key for a model's provider.

        Args:
            model_id: Model ID.

        Returns:
            API key if found, None otherwise.
        """
        provider = self.get_model_provider(model_id)
        if provider is None:
            return None

        return os.environ.get(provider.api_key_env)

    def get_model_capabilities(self, model_id: str) -> Optional[ModelCapability]:
        """Get capabilities for a model.

        Args:
            model_id: Model ID.

        Returns:
            ModelCapability if model found, None otherwise.
        """
        model = self.get_model(model_id)
        return model.capabilities if model else None

    def has_capability(self, model_id: str, capability: str) -> bool:
        """Check if a model has a specific capability.

        Args:
            model_id: Model ID.
            capability: Capability name ("vision", "tools", "streaming").

        Returns:
            True if model has the capability.

        Raises:
            ValueError: If capability name is invalid.
        """
        valid_capabilities = {"vision", "tools", "streaming"}
        if capability not in valid_capabilities:
            raise ValueError(
                f"Invalid capability: {capability}. " f"Valid capabilities: {valid_capabilities}"
            )

        capabilities = self.get_model_capabilities(model_id)
        if capabilities is None:
            return False

        return getattr(capabilities, capability, False)

    def get_provider_type(self, provider_name: str) -> Optional[str]:
        """Get provider type by name.

        Args:
            provider_name: Provider name.

        Returns:
            Provider type if found, None otherwise.
        """
        provider = self._providers.get(provider_name)
        return provider.provider_type if provider else None

    def get_provider_type_for_model(self, model_id: str) -> Optional[str]:
        """Get provider type for a model.

        Args:
            model_id: Model ID.

        Returns:
            Provider type if found, None otherwise.
        """
        provider = self.get_model_provider(model_id)
        return provider.provider_type if provider else None

    def get_base_url(self, provider_name: str) -> Optional[str]:
        """Get base URL for a provider.

        Args:
            provider_name: Provider name.

        Returns:
            Base URL if set, None otherwise.
        """
        provider = self._providers.get(provider_name)
        return provider.base_url if provider else None

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get ModelInfo for a model, including provider context.

        Supports both simple IDs ("gpt-4") and prefixed IDs ("openai/gpt-4").

        Args:
            model_id: Model ID, optionally prefixed with provider name.

        Returns:
            ModelInfo if found, None otherwise.
        """
        result = self._model_index.get(model_id)
        if result is None:
            return None

        provider, model = result
        return ModelInfo(provider=provider.name, model=model)

    def get_models_by_capability(self, capability: str) -> list[ModelInfo]:
        """Get all models that have a specific capability.

        Args:
            capability: Capability name ("vision", "tools", "streaming").

        Returns:
            List of ModelInfo instances that have the specified capability.
        """
        valid_capabilities = {"vision", "tools", "streaming"}
        if capability not in valid_capabilities:
            return []

        result: list[ModelInfo] = []
        seen: set[str] = set()

        for provider_name, provider in self._providers.items():
            for model in provider.models:
                if model.id in seen:
                    continue

                has_cap = getattr(model.capabilities, capability, False)
                if has_cap:
                    result.append(ModelInfo(provider=provider_name, model=model))
                    seen.add(model.id)

        return result
