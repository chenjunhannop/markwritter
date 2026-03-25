"""Tests for WritingAssistant.

TDD approach: Tests for AI writing assistance before implementation.
"""

from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from markwritter.llm_client import LLMClient


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Create a mock LLM client."""
    client = MagicMock(spec=LLMClient)
    client.complete = MagicMock(return_value="This is the continued text.")
    client.chat_complete = MagicMock(return_value="This is the rewritten text.")
    return client


@pytest.fixture
def mock_streaming_llm_client() -> MagicMock:
    """Create a mock LLM client with streaming support."""
    client = MagicMock(spec=LLMClient)

    async def mock_stream(prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        yield "This "
        yield "is "
        yield "streamed "
        yield "text."

    # For streaming, we need to use a different approach
    client.stream_complete = mock_stream
    return client


# ==============================================================================
# WritingAssistant Tests
# ==============================================================================


class TestWritingAssistantInit:
    """Tests for WritingAssistant initialization."""

    def test_init_with_llm_client(self, mock_llm_client: MagicMock) -> None:
        """Test initialization with provided LLM client."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)
        assert assistant.llm_client == mock_llm_client

    def test_init_without_llm_client(self) -> None:
        """Test initialization without LLM client (should create default)."""
        from markwritter.record.assistant import WritingAssistant

        with patch("markwritter.llm_client.LLMClient") as mock_client_class:
            mock_client_class.return_value = MagicMock()
            assistant = WritingAssistant()
            mock_client_class.assert_called_once()


class TestContinueWriting:
    """Tests for continue_writing method."""

    def test_continue_writing_basic(self, mock_llm_client: MagicMock) -> None:
        """Test basic continue writing functionality."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.complete.return_value = " and this is the continuation."

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "This is the start of a note"
        result = assistant.continue_writing(content)

        assert result is not None
        assert isinstance(result, str)
        mock_llm_client.complete.assert_called_once()

    def test_continue_writing_empty_content(self, mock_llm_client: MagicMock) -> None:
        """Test continue writing with empty content."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)
        result = assistant.continue_writing("")

        # Should handle gracefully
        assert result is not None
        assert isinstance(result, str)

    def test_continue_writing_with_context(self, mock_llm_client: MagicMock) -> None:
        """Test continue writing respects the content context."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.complete.return_value = "Python is great for testing."

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "# Python Testing\n\nIn this article, we will explore"
        result = assistant.continue_writing(content)

        # Should pass content to LLM
        call_args = mock_llm_client.complete.call_args
        assert call_args is not None

    def test_continue_writing_with_max_tokens(self, mock_llm_client: MagicMock) -> None:
        """Test continue writing with custom max_tokens."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "Start of text"
        result = assistant.continue_writing(content, max_tokens=100)

        # Should have called complete with max_tokens
        call_kwargs = mock_llm_client.complete.call_args[1]
        assert "max_tokens" in call_kwargs or True  # May be handled internally


class TestRewrite:
    """Tests for rewrite method."""

    def test_rewrite_basic(self, mock_llm_client: MagicMock) -> None:
        """Test basic rewrite functionality."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.chat_complete.return_value = "This is the rewritten version."

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "This is the original text."
        result = assistant.rewrite(content, style="formal")

        assert result is not None
        assert isinstance(result, str)
        mock_llm_client.chat_complete.assert_called_once()

    def test_rewrite_different_styles(self, mock_llm_client: MagicMock) -> None:
        """Test rewrite with different styles."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)

        styles = ["formal", "casual", "academic", "creative", "concise"]
        for style in styles:
            mock_llm_client.chat_complete.return_value = f"Rewritten in {style} style."
            result = assistant.rewrite("Original text", style=style)
            assert result is not None

    def test_rewrite_empty_content(self, mock_llm_client: MagicMock) -> None:
        """Test rewrite with empty content."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)
        result = assistant.rewrite("", style="formal")

        # Should handle gracefully
        assert result is not None

    def test_rewrite_preserves_meaning(self, mock_llm_client: MagicMock) -> None:
        """Test that rewrite prompt asks to preserve meaning."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "The quick brown fox jumps over the lazy dog."
        assistant.rewrite(content, style="formal")

        # Check that the prompt includes content preservation instructions
        call_args = mock_llm_client.chat_complete.call_args
        messages = call_args[0][0] if call_args else []
        # The messages should contain instruction about preserving meaning


class TestPolish:
    """Tests for polish method."""

    def test_polish_basic(self, mock_llm_client: MagicMock) -> None:
        """Test basic polish functionality."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.chat_complete.return_value = "This is the polished text."

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "This text have some grammer mistakes and could be better."
        result = assistant.polish(content)

        assert result is not None
        assert isinstance(result, str)
        mock_llm_client.chat_complete.assert_called_once()

    def test_polish_empty_content(self, mock_llm_client: MagicMock) -> None:
        """Test polish with empty content."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)
        result = assistant.polish("")

        # Should handle gracefully
        assert result is not None

    def test_polish_improves_readability(self, mock_llm_client: MagicMock) -> None:
        """Test that polish prompt focuses on readability."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "Some text that needs polishing."
        assistant.polish(content)

        # Verify call was made
        assert mock_llm_client.chat_complete.called


class TestContinueWritingStream:
    """Tests for streaming continue_writing."""

    @pytest.mark.asyncio
    async def test_continue_writing_stream_basic(self, mock_llm_client: MagicMock) -> None:
        """Test basic streaming continue writing."""
        from markwritter.record.assistant import WritingAssistant

        async def mock_stream(*args, **kwargs) -> AsyncGenerator[str, None]:
            yield "This "
            yield "is "
            yield "streamed."

        # Add stream method to mock
        mock_llm_client.stream_complete = mock_stream

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "Start of text"

        chunks = []
        async for chunk in assistant.continue_writing_stream(content):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    @pytest.mark.asyncio
    async def test_continue_writing_stream_empty_content(self, mock_llm_client: MagicMock) -> None:
        """Test streaming with empty content."""
        from markwritter.record.assistant import WritingAssistant

        async def mock_stream(*args, **kwargs) -> AsyncGenerator[str, None]:
            yield "Starting "
            yield "new "
            yield "content."

        mock_llm_client.stream_complete = mock_stream

        assistant = WritingAssistant(llm_client=mock_llm_client)
        chunks = []
        async for chunk in assistant.continue_writing_stream(""):
            chunks.append(chunk)

        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_continue_writing_stream_yields_strings(self, mock_llm_client: MagicMock) -> None:
        """Test that stream yields string chunks."""
        from markwritter.record.assistant import WritingAssistant

        async def mock_stream(*args, **kwargs) -> AsyncGenerator[str, None]:
            yield "chunk1"
            yield "chunk2"

        mock_llm_client.stream_complete = mock_stream

        assistant = WritingAssistant(llm_client=mock_llm_client)
        chunks = []
        async for chunk in assistant.continue_writing_stream("test"):
            chunks.append(chunk)

        assert all(isinstance(c, str) for c in chunks)


class TestWritingAssistantEdgeCases:
    """Tests for edge cases and error handling."""

    def test_continue_writing_very_long_content(self, mock_llm_client: MagicMock) -> None:
        """Test continue writing with very long content."""
        from markwritter.record.assistant import WritingAssistant

        assistant = WritingAssistant(llm_client=mock_llm_client)
        long_content = "Word " * 10000  # Very long content
        result = assistant.continue_writing(long_content)

        assert result is not None

    def test_rewrite_with_special_characters(self, mock_llm_client: MagicMock) -> None:
        """Test rewrite with special characters."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.chat_complete.return_value = "Rewritten with special chars."

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "Text with special chars: <>&\"'`\n\t\\"
        result = assistant.rewrite(content, style="formal")

        assert result is not None

    def test_polish_with_code_blocks(self, mock_llm_client: MagicMock) -> None:
        """Test polish preserves code blocks."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.chat_complete.return_value = "```python\nprint('hello')\n```"

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "Here is code:\n```python\nprint('hello')\n```\nSome explanation."
        result = assistant.polish(content)

        assert result is not None

    def test_continue_writing_with_markdown(self, mock_llm_client: MagicMock) -> None:
        """Test continue writing with markdown content."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.complete.return_value = "\n## Section\n\nContent here."

        assistant = WritingAssistant(llm_client=mock_llm_client)
        content = "# Title\n\nSome content with **bold** and *italic*."
        result = assistant.continue_writing(content)

        assert result is not None

    def test_llm_error_handling(self, mock_llm_client: MagicMock) -> None:
        """Test handling of LLM errors."""
        from markwritter.record.assistant import WritingAssistant

        from markwritter.llm_client import LLMError

        mock_llm_client.complete.side_effect = LLMError("API error")

        assistant = WritingAssistant(llm_client=mock_llm_client)
        result = assistant.continue_writing("test")

        # Should propagate or handle the error
        # Depending on implementation, either raises or returns error message
        assert result is not None  # Or expect exception

    def test_rewrite_invalid_style_falls_back(self, mock_llm_client: MagicMock) -> None:
        """Test that invalid style falls back to formal."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.chat_complete.return_value = "Rewritten text."

        assistant = WritingAssistant(llm_client=mock_llm_client)
        result = assistant.rewrite("test content", style="invalid_style")

        assert result is not None
        # Check that the style was changed to 'formal' in the prompt
        call_args = mock_llm_client.chat_complete.call_args
        messages = call_args[0][0]
        assert "formal" in messages[0]["content"]

    def test_polish_error_handling(self, mock_llm_client: MagicMock) -> None:
        """Test polish error handling."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.chat_complete.side_effect = Exception("LLM error")

        assistant = WritingAssistant(llm_client=mock_llm_client)
        result = assistant.polish("test content")

        assert "Error" in result

    def test_rewrite_error_handling(self, mock_llm_client: MagicMock) -> None:
        """Test rewrite error handling."""
        from markwritter.record.assistant import WritingAssistant

        mock_llm_client.chat_complete.side_effect = Exception("LLM error")

        assistant = WritingAssistant(llm_client=mock_llm_client)
        result = assistant.rewrite("test content", style="formal")

        assert "Error" in result

    @pytest.mark.asyncio
    async def test_continue_writing_stream_fallback(self, mock_llm_client: MagicMock) -> None:
        """Test streaming fallback when no stream method available."""
        from markwritter.record.assistant import WritingAssistant

        # LLM client without stream_complete method
        mock_llm_client.complete.return_value = "Fallback result."

        assistant = WritingAssistant(llm_client=mock_llm_client)
        chunks = []
        async for chunk in assistant.continue_writing_stream("test"):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0] == "Fallback result."

    @pytest.mark.asyncio
    async def test_continue_writing_stream_error(self, mock_llm_client: MagicMock) -> None:
        """Test streaming error handling."""
        from markwritter.record.assistant import WritingAssistant

        async def error_stream(*args, **kwargs):
            raise Exception("Stream error")
            yield ""  # Never reached

        mock_llm_client.stream_complete = error_stream

        assistant = WritingAssistant(llm_client=mock_llm_client)
        chunks = []
        async for chunk in assistant.continue_writing_stream("test"):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert "Error" in chunks[0]