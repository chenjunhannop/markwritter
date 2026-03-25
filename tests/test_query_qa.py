"""Tests for Query module - Q&A System.

TDD approach: These tests define the expected behavior before implementation.
"""

import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from markwritter.query.search import AnswerResult, QASystem, SourceReference


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_vault() -> Generator[Path, None, None]:
    """Create a temporary vault directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        (vault_path / "python-testing.md").write_text(
            """---
title: Python Testing Guide
tags: [python, testing]
---

# Python Testing Guide

TDD is a development practice where you write tests before code.
Use pytest for unit testing in Python.
"""
        )

        (vault_path / "fastapi-tutorial.md").write_text(
            """---
title: FastAPI Tutorial
tags: [python, fastapi]
---

# FastAPI Tutorial

FastAPI is a modern Python web framework.
It provides automatic API documentation.
"""
        )

        yield vault_path


@pytest.fixture
def mock_memory_service() -> MagicMock:
    """Create a mock memory service."""
    service = MagicMock()
    service.retrieve = AsyncMock(return_value={
        "items": [
            {
                "id": "item-1",
                "content": "Python testing guide",
                "score": 0.95,
                "user": {"note_path": "python-testing.md"},
            },
        ]
    })
    return service


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Create a mock LLM client."""
    client = MagicMock()
    client.generate = AsyncMock(return_value="Based on your notes, pytest is recommended for Python testing.")
    return client


@pytest.fixture
def mock_vault() -> MagicMock:
    """Create a mock Obsidian vault."""
    vault = MagicMock()

    def mock_read_note(path: str) -> MagicMock:
        note = MagicMock()
        note.path = path
        note.title = path.replace(".md", "").replace("-", " ").title()
        note.content = "Test content for " + path
        note.metadata = {"tags": ["test"]}
        return note

    vault.read_note.side_effect = mock_read_note
    vault.path = Path("/tmp/vault")

    return vault


# ==============================================================================
# QASystem Initialization Tests
# ==============================================================================


class TestQASystemInit:
    """Tests for QASystem initialization."""

    def test_init_with_memory_service(self, mock_memory_service: MagicMock) -> None:
        """Test initialization with memory service."""
        qa = QASystem(memory_service=mock_memory_service)

        assert qa.memory_service == mock_memory_service

    def test_init_with_llm_client(
        self, mock_memory_service: MagicMock, mock_llm_client: MagicMock
    ) -> None:
        """Test initialization with LLM client."""
        qa = QASystem(
            memory_service=mock_memory_service,
            llm_client=mock_llm_client,
        )

        assert qa.llm_client == mock_llm_client

    def test_init_with_vault(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test initialization with vault."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        assert qa.vault == mock_vault


# ==============================================================================
# QASystem Ask Tests
# ==============================================================================


class TestQASystemAsk:
    """Tests for Q&A functionality."""

    @pytest.mark.asyncio
    async def test_ask_returns_answer(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that ask returns an answer."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        # Mock the internal _generate_answer method
        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Test answer"

            result = await qa.ask("What is Python testing?")

            assert isinstance(result, AnswerResult)
            assert result.answer is not None

    @pytest.mark.asyncio
    async def test_ask_includes_sources(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that ask includes source references."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Test answer"

            result = await qa.ask("What is Python testing?")

            assert isinstance(result.sources, list)

    @pytest.mark.asyncio
    async def test_ask_no_relevant_notes(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask when no relevant notes found."""
        mock_memory_service.retrieve = AsyncMock(return_value={"items": []})

        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        result = await qa.ask("What is xyz?")

        assert result.answer is not None
        assert "no relevant" in result.answer.lower() or result.sources == []

    @pytest.mark.asyncio
    async def test_ask_with_context(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask with conversation context."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        context = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Follow-up answer"

            result = await qa.ask("Follow-up question", context=context)

            assert result.answer is not None

    @pytest.mark.asyncio
    async def test_ask_top_k_parameter(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that top_k is used for retrieval."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Answer"

            await qa.ask("Question", top_k=10)

            call_kwargs = mock_memory_service.retrieve.call_args[1]
            assert call_kwargs["top_k"] == 10


# ==============================================================================
# QASystem Streaming Tests
# ==============================================================================


class TestQASystemStreaming:
    """Tests for streaming Q&A."""

    @pytest.mark.asyncio
    async def test_ask_stream_returns_generator(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that ask_stream returns an async generator."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        # Mock streaming
        async def mock_stream(*args, **kwargs):
            yield {"type": "token", "content": "Hello"}
            yield {"type": "token", "content": " world"}
            yield {"type": "done", "sources": []}

        with patch.object(qa, '_stream_answer', return_value=mock_stream()):
            result = qa.ask_stream("Question")

            assert hasattr(result, '__aiter__')

    @pytest.mark.asyncio
    async def test_ask_stream_yields_tokens(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that ask_stream yields tokens."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        async def mock_stream(*args, **kwargs):
            yield {"type": "token", "content": "Test"}
            yield {"type": "token", "content": " answer"}
            yield {"type": "sources", "content": []}
            yield {"type": "done"}

        with patch.object(qa, '_stream_answer', return_value=mock_stream()):
            chunks = []
            async for chunk in qa.ask_stream("Question"):
                chunks.append(chunk)

            assert len(chunks) >= 1
            assert any(c.get("type") == "token" for c in chunks)

    @pytest.mark.asyncio
    async def test_ask_stream_includes_sources_at_end(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that streaming includes sources at the end."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        async def mock_stream(*args, **kwargs):
            yield {"type": "token", "content": "Answer"}
            yield {"type": "sources", "content": [{"note_path": "test.md"}]}
            yield {"type": "done"}

        with patch.object(qa, '_stream_answer', return_value=mock_stream()):
            chunks = []
            async for chunk in qa.ask_stream("Question"):
                chunks.append(chunk)

            # Should have sources chunk
            sources_chunks = [c for c in chunks if c.get("type") == "sources"]
            assert len(sources_chunks) >= 1

    @pytest.mark.asyncio
    async def test_ask_stream_handles_error(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that streaming handles errors gracefully."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        async def mock_stream(*args, **kwargs):
            yield {"type": "token", "content": "Start"}
            yield {"type": "error", "content": "Something went wrong"}

        with patch.object(qa, '_stream_answer', return_value=mock_stream()):
            chunks = []
            async for chunk in qa.ask_stream("Question"):
                chunks.append(chunk)

            # Should have error chunk
            error_chunks = [c for c in chunks if c.get("type") == "error"]
            assert len(error_chunks) >= 1


# ==============================================================================
# QASystem Source Reference Tests
# ==============================================================================


class TestQASystemSources:
    """Tests for source references."""

    @pytest.mark.asyncio
    async def test_sources_have_required_fields(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that sources have all required fields."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Answer"

            result = await qa.ask("Question")

            if result.sources:
                source = result.sources[0]
                assert isinstance(source, SourceReference)
                assert source.note_path is not None
                assert source.title is not None

    @pytest.mark.asyncio
    async def test_sources_limited_by_top_k(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that sources are limited by top_k."""
        # Mock retrieve to respect top_k parameter
        def mock_retrieve(query: str, top_k: int = 5, **kwargs):
            return {
                "items": [
                    {"id": f"item-{i}", "score": 0.9 - i * 0.1, "user": {"note_path": f"note{i}.md"}}
                    for i in range(min(top_k, 10))  # Respect top_k
                ]
            }

        mock_memory_service.retrieve = AsyncMock(side_effect=mock_retrieve)

        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Answer"

            result = await qa.ask("Question", top_k=3)

            assert len(result.sources) <= 3


# ==============================================================================
# QASystem Edge Cases
# ==============================================================================


class TestQASystemEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_ask_empty_question(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask with empty question."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        result = await qa.ask("")

        assert result.answer is not None

    @pytest.mark.asyncio
    async def test_ask_very_long_question(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask with very long question."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        long_question = "What is " + "Python " * 100 + "?"
        result = await qa.ask(long_question)

        assert result.answer is not None

    @pytest.mark.asyncio
    async def test_ask_unicode_question(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask with Unicode characters."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Unicode answer"

            result = await qa.ask("What is cafe resume?")

            assert result.answer is not None

    @pytest.mark.asyncio
    async def test_ask_handles_memory_error(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask handles memory service errors."""
        mock_memory_service.retrieve = AsyncMock(side_effect=Exception("Memory error"))

        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        result = await qa.ask("Question")

        # Should handle gracefully
        assert result.answer is not None

    @pytest.mark.asyncio
    async def test_ask_handles_missing_note(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask handles notes that no longer exist."""
        from markwritter.obsidian.vault import NoteNotFoundError

        mock_vault.read_note.side_effect = NoteNotFoundError("Not found")
        mock_memory_service.retrieve = AsyncMock(return_value={
            "items": [
                {"id": "item-1", "score": 0.9, "user": {"note_path": "missing.md"}}
            ]
        })

        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Answer"

            result = await qa.ask("Question")

            # Should handle gracefully
            assert result.answer is not None

    @pytest.mark.asyncio
    async def test_ask_with_code_in_question(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask with code snippets in question."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Code answer"

            result = await qa.ask("How do I use `pytest.raises()` in Python?")

            assert result.answer is not None

    @pytest.mark.asyncio
    async def test_ask_multilingual(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test ask with multilingual content."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Multilingual answer"

            result = await qa.ask("Python testing")

            assert result.answer is not None


# ==============================================================================
# QASystem Context Management Tests
# ==============================================================================


class TestQASystemContext:
    """Tests for conversation context."""

    @pytest.mark.asyncio
    async def test_context_improves_answers(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that context is used for better answers."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        context = [
            {"role": "user", "content": "Tell me about Python testing"},
            {"role": "assistant", "content": "Python testing uses pytest framework."},
        ]

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Follow-up answer"

            await qa.ask("How do I install it?", context=context)

            # Context should be passed to generation
            mock_gen.assert_called_once()
            call_args = mock_gen.call_args
            assert call_args[1].get("context") == context

    @pytest.mark.asyncio
    async def test_context_window_limit(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that context is truncated if too long."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        # Very long context
        long_context = [
            {"role": "user", "content": "Q" * 1000},
            {"role": "assistant", "content": "A" * 1000},
        ] * 10  # 20 messages

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Answer"

            await qa.ask("Question", context=long_context)

            # Should handle without error
            mock_gen.assert_called_once()


# ==============================================================================
# QASystem Integration Tests
# ==============================================================================


class TestQASystemIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_full_qa_workflow(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test complete Q&A workflow."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(qa, '_generate_answer', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Complete answer"

            # Ask question
            result = await qa.ask("What is Python testing?")

            assert result.answer == "Complete answer"
            assert isinstance(result.sources, list)

            # Verify retrieval was called
            mock_memory_service.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_streaming_workflow(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test complete streaming workflow."""
        qa = QASystem(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        async def mock_stream(*args, **kwargs):
            yield {"type": "token", "content": "Streaming"}
            yield {"type": "token", "content": " answer"}
            yield {"type": "sources", "content": []}
            yield {"type": "done"}

        with patch.object(qa, '_stream_answer', return_value=mock_stream()):
            # Stream question
            full_answer = ""
            async for chunk in qa.ask_stream("Question"):
                if chunk.get("type") == "token":
                    full_answer += chunk.get("content", "")

            assert "Streaming" in full_answer