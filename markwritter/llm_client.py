"""LiteLLM client with caching, provider registry support, and fallback mechanism."""

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional, Protocol

from markwritter.config import get_config
from markwritter.models import LLMConfig


@dataclass
class CacheEntry:
    """Cache entry with TTL."""

    value: str
    expires_at: float


class MemoryCache:
    """Simple in-memory cache with TTL and size limit."""

    def __init__(self, max_size: int, ttl_seconds: int) -> None:
        """Initialize memory cache.

        Args:
            max_size: Maximum number of entries in cache
            ttl_seconds: Time to live in seconds for each entry
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()

    def get(self, key: str) -> Optional[str]:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        self._cleanup_expired()

        if key not in self._cache:
            return None

        entry = self._cache[key]
        if time.time() > entry.expires_at:
            del self._cache[key]
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return entry.value

    def set(self, key: str, value: str) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cleanup_expired()

        # Remove if exists (to update order)
        if key in self._cache:
            del self._cache[key]

        # Add new entry
        expires_at = time.time() + self.ttl_seconds
        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

        # Enforce size limit (remove oldest)
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        now = time.time()
        expired_keys = [key for key, entry in self._cache.items() if now > entry.expires_at]
        for key in expired_keys:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all entries from cache."""
        self._cache.clear()

    def size(self) -> int:
        """Get current cache size."""
        self._cleanup_expired()
        return len(self._cache)


class LLMError(Exception):
    """LLM API error."""

    pass


class ModelInfo(Protocol):
    """Protocol for model information from registry."""

    @property
    def provider(self) -> str:
        """Provider name."""
        ...

    @property
    def model_id(self) -> str:
        """Model identifier."""
        ...

    @property
    def capabilities(self) -> list[str]:
        """List of capabilities this model supports."""
        ...

    @property
    def full_name(self) -> str:
        """Full model name in provider/model format."""
        ...


class ProviderRegistry(Protocol):
    """Protocol for provider registry interface."""

    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get model info by name.

        Supports formats:
        - 'provider/model' (full format)
        - 'model' (short format, searches all providers)
        """
        ...

    def get_models_by_capability(self, capability: str) -> list[ModelInfo]:
        """Get all models that have a specific capability."""
        ...


class LLMClient:
    """LiteLLM client with caching, retry logic, and provider registry support."""

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        registry: Optional[ProviderRegistry] = None,
    ) -> None:
        """Initialize LLM client.

        Args:
            config: LLM configuration. If None, loads from config file.
            registry: Optional provider registry for model resolution and capability selection.
        """
        self.config = config or get_config().llm
        self.cache: Optional[MemoryCache] = None

        # Initialize cache if enabled
        cache_config = get_config().cache
        if cache_config.enabled:
            self.cache = MemoryCache(
                max_size=cache_config.max_size,
                ttl_seconds=cache_config.ttl_seconds,
            )

        # Initialize registry if not provided
        if registry is not None:
            self.registry = registry
        else:
            # Auto-create ProviderRegistry from config
            from markwritter.provider_registry import (
                ProviderRegistry as ConcreteProviderRegistry,
            )

            self.registry = ConcreteProviderRegistry(self.config)

    def _generate_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _parse_model_string(self, model: str) -> tuple[Optional[str], str]:
        """Parse model string into provider and model_id components.

        Args:
            model: Model string, either 'provider/model' or just 'model'

        Returns:
            Tuple of (provider, model_id). Provider is None if not specified.

        Raises:
            ValueError: If model string is empty
        """
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")

        model = model.strip()

        if "/" in model:
            parts = model.split("/", 1)
            return parts[0].strip(), parts[1].strip()

        return None, model

    def _resolve_model(self, model: str) -> str:
        """Resolve model name to full provider/model format.

        Args:
            model: Model name (can be short or full format)

        Returns:
            Full model name in provider/model format
        """
        # If already has provider prefix, return as-is
        if "/" in model:
            return model

        # Try to resolve via registry
        if self.registry:
            model_info = self.registry.get_model_info(model)
            if model_info:
                return model_info.full_name

        # Return original if no resolution possible
        return model

    def _get_fallback_chain(
        self,
        model: str,
        fallback_models: Optional[list[str]] = None,
    ) -> list[str]:
        """Build ordered list of models to try.

        Args:
            model: Primary model name
            fallback_models: Optional list of fallback model names

        Returns:
            Ordered list of model names to try (deduplicated)
        """
        models_to_try: list[str] = []

        # Resolve and add primary model
        resolved_primary = self._resolve_model(model)
        models_to_try.append(resolved_primary)

        # Add fallbacks
        if fallback_models:
            for fb in fallback_models:
                resolved_fb = self._resolve_model(fb)
                if resolved_fb not in models_to_try:
                    models_to_try.append(resolved_fb)

        return models_to_try

    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        fallback_models: Optional[list[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send completion request to LLM with fallback support.

        Args:
            prompt: The prompt to send
            model: Model to use (defaults to config). Can be 'provider/model' or just 'model'.
            provider: Optional provider prefix to add to model name.
            fallback_models: Optional list of fallback models to try if primary fails.
            temperature: Temperature (defaults to config)
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response text

        Raises:
            LLMError: If all API calls fail
        """
        import litellm

        # Resolve model name
        model = model or self.config.default_model

        # Add provider prefix if specified and model doesn't already have one
        if provider and "/" not in model:
            model = f"{provider}/{model}"

        temperature = temperature if temperature is not None else self.config.temperature

        # Build fallback chain
        models_to_try = self._get_fallback_chain(model, fallback_models)

        # Track errors for each model
        failed_models: list[tuple[str, Exception]] = []

        for current_model in models_to_try:
            # Check cache first
            if self.cache:
                cache_key = self._generate_cache_key(prompt, current_model)
                cached = self.cache.get(cache_key)
                if cached:
                    return cached

            # Prepare request
            messages = [{"role": "user", "content": prompt}]
            kwargs: dict[str, Any] = {
                "model": current_model,
                "messages": messages,
                "temperature": temperature,
                "timeout": self.config.timeout,
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            # Retry logic for this model
            last_error: Optional[Exception] = None
            for attempt in range(self.config.max_retries + 1):
                try:
                    response = litellm.completion(**kwargs)
                    content = response.choices[0].message.content or ""

                    # Cache successful response
                    if self.cache:
                        cache_key = self._generate_cache_key(prompt, current_model)
                        self.cache.set(cache_key, content)

                    return content

                except Exception as e:
                    last_error = e
                    if attempt < self.config.max_retries:
                        time.sleep(2**attempt)  # Exponential backoff
                        continue
                    break

            # This model failed, record error and try next
            if last_error:
                failed_models.append((current_model, last_error))

        # All models failed
        error_details = "; ".join(f"{m}: {str(e)[:100]}" for m, e in failed_models)
        raise LLMError(
            f"All models in fallback chain failed. Tried: {models_to_try}. Errors: {error_details}"
        )

    def complete_with_capability(
        self,
        prompt: str,
        required_capability: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        fallback_models: Optional[list[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Complete request with automatic model selection based on capability.

        If model is specified, it overrides capability-based selection.
        Otherwise, selects the first model with the required capability.

        Args:
            prompt: The prompt to send
            required_capability: Capability required (e.g., 'vision', 'function_calling')
            model: Optional explicit model (overrides capability selection)
            provider: Optional provider prefix
            fallback_models: Optional fallback models
            temperature: Temperature setting
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response text

        Raises:
            LLMError: If no model has the required capability or all calls fail
        """
        # If explicit model provided, use standard complete
        if model:
            return self.complete(
                prompt=prompt,
                model=model,
                provider=provider,
                fallback_models=fallback_models,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        # Require registry for capability-based selection
        if not self.registry:
            raise LLMError(
                "Registry required for capability-based model selection. "
                "Please provide a registry when initializing LLMClient."
            )

        # Find models with required capability
        capable_models = self.registry.get_models_by_capability(required_capability)

        if not capable_models:
            raise LLMError(f"No model found with capability: {required_capability}")

        # Use first capable model as primary
        primary_model = capable_models[0].full_name

        # Build fallback list from remaining capable models
        if not fallback_models:
            fallback_models = [m.full_name for m in capable_models[1:]]

        return self.complete(
            prompt=prompt,
            model=primary_model,
            provider=provider,
            fallback_models=fallback_models,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def chat_complete(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send chat completion request to LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (defaults to config)
            temperature: Temperature (defaults to config)
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response text

        Raises:
            LLMError: If API call fails after retries
        """
        import litellm

        model = model or self.config.default_model
        temperature = temperature if temperature is not None else self.config.temperature

        # Check cache (use last message content as key)
        if self.cache and messages:
            cache_key = self._generate_cache_key(messages[-1].get("content", ""), model)
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "timeout": self.config.timeout,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        last_error: Optional[Exception] = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = litellm.completion(**kwargs)
                content = response.choices[0].message.content or ""

                if self.cache and messages:
                    cache_key = self._generate_cache_key(messages[-1].get("content", ""), model)
                    self.cache.set(cache_key, content)

                return content

            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    time.sleep(2**attempt)
                    continue
                break

        raise LLMError(
            f"LLM API failed after {self.config.max_retries + 1} attempts: {last_error}"
        ) from last_error

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dict with 'size' and 'max_size' keys
        """
        if self.cache is None:
            return {"size": 0, "max_size": 0}
        return {"size": self.cache.size(), "max_size": self.cache.max_size}
