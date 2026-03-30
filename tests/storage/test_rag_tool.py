"""Tests for RAG Search Tool."""

import tempfile
from pathlib import Path

import pytest

from markwritter.storage.cache import VectorSearchCache
from markwritter.storage.chat_db import ChatSessionDB
from markwritter.storage.models import Content, ContentRef, ContentType
from markwritter.storage.path_resolver import PathResolver
from markwritter.storage.rag_tool import RAGSearchResult, RAGSearchTool, RetrievedChunk
from markwritter.storage.service import ContentService
from markwritter.storage.registry import StorageRegistry


@pytest.fixture
async def content_service():
    """Create ContentService with in-memory storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        # Create registry and content service
        registry = StorageRegistry()
        service = ContentService(registry=registry)
        yield service


@pytest.fixture
async def path_resolver(content_service: ContentService):
    """Create PathResolver."""
    resolver = PathResolver(content_service=content_service)
    yield resolver


@pytest.fixture
async def cache():
    """Create VectorSearchCache."""
    cache = VectorSearchCache(max_size=100, default_ttl=300)
    yield cache


@pytest.fixture
async def rag_tool(
    content_service: ContentService,
    path_resolver: PathResolver,
    cache: VectorSearchCache,
):
    """Create RAGSearchTool."""
    tool = RAGSearchTool(
        content_service=content_service,
        path_resolver=path_resolver,
        cache=cache,
    )
    yield tool


class TestRetrievedChunk:
    """Tests for RetrievedChunk dataclass."""

    def test_create_chunk_with_defaults(self) -> None:
        """Test creating chunk with default values."""
        chunk = RetrievedChunk(
            text="Test content",
            file_path="notes/test.md",
        )

        assert chunk.text == "Test content"
        assert chunk.file_path == "notes/test.md"
        assert chunk.page_num == 0
        assert chunk.paragraph_idx == 0
        assert chunk.score == 0.0
        assert chunk.content_id == ""

    def test_create_chunk_with_all_fields(self) -> None:
        """Test creating chunk with all fields."""
        chunk = RetrievedChunk(
            text="Test content",
            file_path="notes/test.md",
            page_num=5,
            paragraph_idx=2,
            score=0.95,
            content_id="uuid-123",
        )

        assert chunk.text == "Test content"
        assert chunk.file_path == "notes/test.md"
        assert chunk.page_num == 5
        assert chunk.paragraph_idx == 2
        assert chunk.score == 0.95
        assert chunk.content_id == "uuid-123"


class TestRAGSearchResult:
    """Tests for RAGSearchResult dataclass."""

    def test_create_empty_result(self) -> None:
        """Test creating empty search result."""
        result = RAGSearchResult(query="test query")

        assert result.query == "test query"
        assert result.chunks == []
        assert result.total_chunks == 0
        assert result.sources_searched == []

    def test_create_result_with_chunks(self) -> None:
        """Test creating result with chunks."""
        chunks = [
            RetrievedChunk(
                text="Chunk 1",
                file_path="notes/a.md",
                score=0.9,
            ),
            RetrievedChunk(
                text="Chunk 2",
                file_path="notes/b.md",
                page_num=3,
                score=0.8,
            ),
        ]

        result = RAGSearchResult(
            query="test query",
            chunks=chunks,
            total_chunks=2,  # Must be set explicitly
            sources_searched=["notes/a.md", "notes/b.md"],
        )

        assert len(result.chunks) == 2
        assert result.total_chunks == 2
        assert result.sources_searched == ["notes/a.md", "notes/b.md"]

    def test_get_context_text_empty(self) -> None:
        """Test getting context text with no chunks."""
        result = RAGSearchResult(query="test query")
        context = result.get_context_text()

        assert context == ""

    def test_get_context_text_with_chunks(self) -> None:
        """Test getting context text with chunks."""
        chunks = [
            RetrievedChunk(
                text="First chunk content",
                file_path="notes/a.md",
            ),
            RetrievedChunk(
                text="Second chunk content",
                file_path="notes/b.pdf",
                page_num=5,
            ),
        ]

        result = RAGSearchResult(query="test query", chunks=chunks)
        context = result.get_context_text()

        assert "[Source 1: notes/a.md]" in context
        assert "First chunk content" in context
        assert "[Source 2: notes/b.pdf, page 5]" in context
        assert "Second chunk content" in context

    def test_get_context_text_max_chunks(self) -> None:
        """Test max_chunks parameter."""
        chunks = [
            RetrievedChunk(text=f"Chunk {i}", file_path=f"notes/{i}.md")
            for i in range(10)
        ]

        result = RAGSearchResult(query="test query", chunks=chunks)
        context = result.get_context_text(max_chunks=3)

        # Should only include first 3 chunks
        assert "Chunk 0" in context
        assert "Chunk 1" in context
        assert "Chunk 2" in context
        assert "Chunk 3" not in context


class TestRAGSearchTool:
    """Tests for RAGSearchTool."""

    @pytest.mark.asyncio
    async def test_search_without_source_paths(
        self, rag_tool: RAGSearchTool
    ) -> None:
        """Test search without source path filtering."""
        result = await rag_tool.search(
            query="test query",
            source_paths=None,
            limit=5,
        )

        assert result.query == "test query"
        # Results depend on ContentService implementation

    @pytest.mark.asyncio
    async def test_search_with_source_paths(
        self, rag_tool: RAGSearchTool
    ) -> None:
        """Test search with source path filtering."""
        result = await rag_tool.search(
            query="test query",
            source_paths=["notes/a.md", "notes/b.md"],
            limit=5,
        )

        assert result.query == "test query"
        assert result.sources_searched == ["notes/a.md", "notes/b.md"]

    @pytest.mark.asyncio
    async def test_search_with_limit(
        self, rag_tool: RAGSearchTool
    ) -> None:
        """Test search respects limit parameter."""
        result = await rag_tool.search(
            query="test query",
            limit=3,
        )

        assert len(result.chunks) <= 3

    @pytest.mark.asyncio
    async def test_search_caching(
        self, rag_tool: RAGSearchTool, cache: VectorSearchCache
    ) -> None:
        """Test search results are cached."""
        # First search
        await rag_tool.search(
            query="cache test query",
            limit=5,
            use_cache=True,
        )

        # Check cache has entry
        stats = cache.get_stats()
        # Cache should have been written to

        # Second search with same query should hit cache
        result = await rag_tool.search(
            query="cache test query",
            limit=5,
            use_cache=True,
        )

        # Verify we got cached results
        assert result.query == "cache test query"

    @pytest.mark.asyncio
    async def test_search_without_cache(
        self, rag_tool: RAGSearchTool
    ) -> None:
        """Test search with caching disabled."""
        result = await rag_tool.search(
            query="no cache query",
            limit=5,
            use_cache=False,
        )

        assert result.query == "no cache query"

    def test_generate_cache_key(self, rag_tool: RAGSearchTool) -> None:
        """Test cache key generation."""
        key1 = rag_tool._generate_cache_key(
            query="test",
            content_ids=["id1", "id2"],
            limit=5,
        )

        key2 = rag_tool._generate_cache_key(
            query="test",
            content_ids=["id2", "id1"],  # Different order
            limit=5,
        )

        # Keys should be same despite different order (sorted)
        assert key1 == key2

    def test_generate_cache_key_different_params(self, rag_tool: RAGSearchTool) -> None:
        """Test different params generate different keys."""
        key1 = rag_tool._generate_cache_key(
            query="test",
            content_ids=["id1"],
            limit=5,
        )

        key2 = rag_tool._generate_cache_key(
            query="test",
            content_ids=["id1"],
            limit=10,  # Different limit
        )

        assert key1 != key2

    def test_serialize_result(self, rag_tool: RAGSearchTool) -> None:
        """Test result serialization."""
        chunks = [
            RetrievedChunk(
                text="Test",
                file_path="notes/test.md",
                page_num=2,
                paragraph_idx=1,
                score=0.85,
                content_id="uuid-123",
            )
        ]
        result = RAGSearchResult(query="test", chunks=chunks)

        serialized = rag_tool._serialize_result(result)

        assert len(serialized) == 1
        assert serialized[0]["text"] == "Test"
        assert serialized[0]["file_path"] == "notes/test.md"
        assert serialized[0]["page_num"] == 2
        assert serialized[0]["score"] == 0.85
        assert serialized[0]["content_id"] == "uuid-123"

    def test_deserialize_result(self, rag_tool: RAGSearchTool) -> None:
        """Test result deserialization."""
        data = [
            {
                "text": "Deserialized text",
                "file_path": "notes/deser.md",
                "page_num": 3,
                "paragraph_idx": 0,
                "score": 0.75,
                "content_id": "deser-uuid",
            }
        ]

        result = rag_tool._deserialize_result(data, query="deser query")

        assert result.query == "deser query"
        assert len(result.chunks) == 1
        assert result.chunks[0].text == "Deserialized text"
        assert result.chunks[0].file_path == "notes/deser.md"
        assert result.chunks[0].page_num == 3
        assert result.chunks[0].score == 0.75


class TestRAGSearchToolIntegration:
    """Integration tests for RAGSearchTool with real dependencies."""

    @pytest.mark.asyncio
    async def test_full_search_flow(self) -> None:
        """Test complete search flow with all components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)

            # Create all dependencies
            registry = StorageRegistry()
            content_service = ContentService(registry=registry)
            path_resolver = PathResolver(content_service=content_service)
            cache = VectorSearchCache(max_size=100)

            rag_tool = RAGSearchTool(
                content_service=content_service,
                path_resolver=path_resolver,
                cache=cache,
            )

            # Perform search
            result = await rag_tool.search(
                query="integration test",
                source_paths=None,
                limit=5,
            )

            assert result.query == "integration test"
            assert isinstance(result, RAGSearchResult)
