"""LiteLLM client with caching and error handling."""

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

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


class LLMClient:
    """LiteLLM client with caching and retry logic."""

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize LLM client.

        Args:
            config: LLM configuration. If None, loads from config file.
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

    def _generate_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send completion request to LLM.

        Args:
            prompt: The prompt to send
            model: Model to use (defaults to config)
            temperature: Temperature (defaults to config)
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response text

        Raises:
            LLMError: If API call fails after retries
        """
        import litellm

        # Use configured defaults
        model = model or self.config.default_model
        temperature = temperature if temperature is not None else self.config.temperature

        # Check cache first
        if self.cache:
            cache_key = self._generate_cache_key(prompt, model)
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        # Prepare request
        messages = [{"role": "user", "content": prompt}]
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "timeout": self.config.timeout,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        # Retry logic
        last_error: Optional[Exception] = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = litellm.completion(**kwargs)
                content = response.choices[0].message.content or ""

                # Cache successful response
                if self.cache:
                    cache_key = self._generate_cache_key(prompt, model)
                    self.cache.set(cache_key, content)

                return content

            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                break

        raise LLMError(
            f"LLM API failed after {self.config.max_retries + 1} attempts: {last_error}"
        ) from last_error

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
