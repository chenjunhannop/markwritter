"""LLM service for LLM operations.

Phase 3.3: Service layer implementation for LLM operations.
Provides a clean interface for LLM completion operations with proper error handling.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from markwritter.llm_client import LLMClient

logger = logging.getLogger(__name__)


class LLMResult(BaseModel):
    """Result of an LLM operation."""

    success: bool
    content: str = ""
    message: str = ""


class LLMService:
    """Service for LLM operations.

    Provides a clean interface for LLM operations with:
    - Proper error handling
    - Dependency injection support
    - Input validation
    """

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        """Initialize the LLM service.

        Args:
            llm_client: LLMClient instance for LLM operations.
        """
        if llm_client is None:
            from markwritter.llm_client import LLMClient

            llm_client = LLMClient()

        self._llm_client = llm_client

    @property
    def llm_client(self) -> LLMClient:
        """Get the LLM client instance."""
        return self._llm_client

    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        fallback_models: Optional[list[str]] = None,
    ) -> LLMResult:
        """Send a completion request.

        Args:
            prompt: The prompt to send
            model: Model to use
            provider: Optional provider prefix
            temperature: Temperature setting
            max_tokens: Maximum tokens to generate
            fallback_models: Optional list of fallback models

        Returns:
            LLMResult with operation status
        """
        try:
            kwargs: dict[str, Any] = {}
            if model is not None:
                kwargs["model"] = model
            if provider is not None:
                kwargs["provider"] = provider
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            if fallback_models is not None:
                kwargs["fallback_models"] = fallback_models

            content = self._llm_client.complete(prompt=prompt, **kwargs)

            return LLMResult(
                success=True,
                content=content,
            )
        except Exception as e:
            logger.error(f"Error in LLM complete: {e}")
            return LLMResult(
                success=False,
                message=str(e),
            )

    def chat_complete(
        self,
        messages: Optional[list[dict[str, str]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResult:
        """Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use
            temperature: Temperature setting
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResult with operation status
        """
        if messages is None:
            return LLMResult(
                success=False,
                message="Messages are required for chat completion",
            )

        try:
            kwargs: dict[str, Any] = {}
            if model is not None:
                kwargs["model"] = model
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            content = self._llm_client.chat_complete(messages=messages, **kwargs)

            return LLMResult(
                success=True,
                content=content,
            )
        except Exception as e:
            logger.error(f"Error in LLM chat_complete: {e}")
            return LLMResult(
                success=False,
                message=str(e),
            )

    async def stream_complete(
        self,
        messages: Optional[list[dict[str, str]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion request."""
        if messages is None:
            raise ValueError("Messages are required for chat completion")

        kwargs: dict[str, Any] = {}
        if model is not None:
            kwargs["model"] = model
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if api_base is not None:
            kwargs["api_base"] = api_base
        if api_key is not None:
            kwargs["api_key"] = api_key

        async for token in self._llm_client.stream_complete(messages=messages, **kwargs):
            yield token

    def complete_with_capability(
        self,
        prompt: str,
        capability: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        fallback_models: Optional[list[str]] = None,
    ) -> LLMResult:
        """Send a completion request with capability requirement.

        Args:
            prompt: The prompt to send
            capability: Required capability (e.g., 'vision', 'function_calling')
            model: Optional explicit model
            provider: Optional provider prefix
            temperature: Temperature setting
            max_tokens: Maximum tokens to generate
            fallback_models: Optional fallback models

        Returns:
            LLMResult with operation status
        """
        try:
            kwargs: dict[str, Any] = {}
            if model is not None:
                kwargs["model"] = model
            if provider is not None:
                kwargs["provider"] = provider
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            if fallback_models is not None:
                kwargs["fallback_models"] = fallback_models

            content = self._llm_client.complete_with_capability(
                prompt=prompt,
                required_capability=capability,
                **kwargs,
            )

            return LLMResult(
                success=True,
                content=content,
            )
        except Exception as e:
            logger.error(f"Error in LLM complete_with_capability: {e}")
            return LLMResult(
                success=False,
                message=str(e),
            )
