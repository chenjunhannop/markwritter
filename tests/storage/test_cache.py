"""Tests for VectorSearchCache.

Tests for LRU cache implementation for vector search results.
"""

import asyncio
import time
from unittest.mock import MagicMock

import pytest

from markwritter.storage.cache import (
    CacheEntry,
    VectorSearchCache,
    get_global_cache,
)
from markwritter.storage.models import ContentRef, ContentType, StorageBackend


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_results() -> list[ContentRef]:
    """Create sample search results."""
    return [
        ContentRef(
            id="result-1",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            title="Note 1",
            path="notes/note1.md",
        ),
        ContentRef(
            id="result-2",
            source_type=ContentType.PDF,
            storage_backend=StorageBackend.OBSIDIAN,
            title="Document 2",
            path="docs/doc2.pdf",
        ),
    ]


@pytest.fixture
def cache() -> VectorSearchCache:
    """Create a VectorSearchCache instance."""
    return VectorSearchCache(max_size=5, default_ttl=300)


# ==============================================================================
# CacheEntry Tests
# ==============================================================================


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_entry_without_ttl_never_expires(self) -> None:
        """Test entry without TTL never expires."""
        entry = CacheEntry(results=[], ttl_seconds=None)
        assert entry.is_expired() is False

    def test_entry_with_ttl_not_expired(self) -> None:
        """Test entry with TTL not expired."""
        entry = CacheEntry(results=[], ttl_seconds=60)
        # Freshly created, should not be expired
        assert entry.is_expired() is False

    def test_entry_with_ttl_expired(self) -> None:
        """Test entry with TTL expired."""
        entry = CacheEntry(results=[], ttl_seconds=0.001, created_at=time.time() - 1)
        assert entry.is_expired() is True


# ==============================================================================
# Basic Cache Operations Tests
# ==============================================================================


class TestBasicOperations:
    """Tests for basic cache operations."""

    @pytest.mark.asyncio
    async def test_cache_miss(self, cache: VectorSearchCache) -> None:
        """Test cache miss returns None."""
        result = await cache.get("nonexistent-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_hit(self, cache: VectorSearchCache, sample_results) -> None:
        """Test cache hit returns cached results."""
        await cache.set("test-key", sample_results)
        result = await cache.get("test-key")

        assert result is not None
        assert len(result) == 2
        assert result[0].id == "result-1"
        assert result[1].id == "result-2"

    @pytest.mark.asyncio
    async def test_cache_set_overwrites(
        self, cache: VectorSearchCache, sample_results
    ) -> None:
        """Test that set overwrites existing entry."""
        new_results = [
            ContentRef(
                id="new-result",
                source_type=ContentType.MARKDOWN,
                storage_backend=StorageBackend.OBSIDIAN,
            )
        ]

        await cache.set("test-key", sample_results)
        await cache.set("test-key", new_results)

        result = await cache.get("test-key")
        assert result is not None
        assert len(result) == 1
        assert result[0].id == "new-result"

    @pytest.mark.asyncio
    async def test_cache_invalidate(self, cache: VectorSearchCache) -> None:
        """Test cache invalidation."""
        await cache.set("to-delete", [])
        await cache.set("to-keep", [])

        result = await cache.invalidate("to-delete")
        assert result is True

        # Verify deleted
        assert await cache.get("to-delete") is None
        # Verify other entry still exists
        assert await cache.get("to-keep") is not None

    @pytest.mark.asyncio
    async def test_cache_invalidate_nonexistent(
        self, cache: VectorSearchCache
    ) -> None:
        """Test invalidating non-existent key returns False."""
        result = await cache.invalidate("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_cache_clear(self, cache: VectorSearchCache) -> None:
        """Test cache clear removes all entries."""
        await cache.set("key1", [])
        await cache.set("key2", [])
        await cache.set("key3", [])

        await cache.clear()

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
        assert await cache.get("key3") is None


# ==============================================================================
# LRU Eviction Tests
# ==============================================================================


class TestLRUEviction:
    """Tests for LRU eviction policy."""

    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache: VectorSearchCache) -> None:
        """Test LRU eviction when cache is full."""
        # Fill cache (max_size=5)
        for i in range(5):
            await cache.set(f"key-{i}", [])

        # Add one more - should evict oldest (key-0)
        await cache.set("key-new", [])

        assert await cache.get("key-0") is None  # Evicted
        assert await cache.get("key-new") is not None  # Added

    @pytest.mark.asyncio
    async def test_lru_access_prevents_eviction(
        self, cache: VectorSearchCache
    ) -> None:
        """Test that accessing an item makes it recently used."""
        # Fill cache
        for i in range(5):
            await cache.set(f"key-{i}", [])

        # Access key-0 (makes it most recently used)
        await cache.get("key-0")

        # Add new item - should evict key-1 (now oldest)
        await cache.set("key-new", [])

        # key-0 should still exist (was accessed)
        assert await cache.get("key-0") is not None
        # key-1 should be evicted (was oldest after access)
        assert await cache.get("key-1") is None


# ==============================================================================
# TTL Tests
# ==============================================================================


class TestTTL:
    """Tests for TTL expiration."""

    @pytest.mark.asyncio
    async def test_ttl_expiration(self) -> None:
        """Test that entries expire after TTL."""
        cache = VectorSearchCache(max_size=10, default_ttl=0.1)  # 100ms TTL

        await cache.set("expires-soon", [])
        assert await cache.get("expires-soon") is not None  # Not expired yet

        # Wait for expiration
        await asyncio.sleep(0.2)

        assert await cache.get("expires-soon") is None  # Expired

    @pytest.mark.asyncio
    async def test_custom_ttl_override(
        self, cache: VectorSearchCache, sample_results
    ) -> None:
        """Test custom TTL override."""
        # Set with custom TTL
        await cache.set("custom-ttl", sample_results, ttl=600)  # 10 minutes

        result = await cache.get("custom-ttl")
        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_no_ttl_entries_never_expire(self) -> None:
        """Test entries without TTL never expire."""
        cache = VectorSearchCache(max_size=10, default_ttl=None)

        await cache.set("permanent", [])

        # Wait a bit
        await asyncio.sleep(0.1)

        # Should still exist
        assert await cache.get("permanent") is not None


# ==============================================================================
# Statistics Tests
# ==============================================================================


class TestStatistics:
    """Tests for cache statistics."""

    @pytest.mark.asyncio
    async def test_hit_miss_tracking(self, cache: VectorSearchCache) -> None:
        """Test that hits and misses are tracked."""
        # Miss
        await cache.get("miss")

        # Set and hit
        await cache.set("hit-key", [])
        await cache.get("hit-key")

        stats = cache.get_stats()

        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_hit_rate_calculation(self, cache: VectorSearchCache) -> None:
        """Test hit rate calculation."""
        # 3 misses
        for i in range(3):
            await cache.get(f"miss-{i}")

        # 2 hits
        await cache.set("hit1", [])
        await cache.set("hit2", [])
        await cache.get("hit1")
        await cache.get("hit2")

        stats = cache.get_stats()

        # 2 hits, 3 misses = 40% hit rate
        assert stats["hits"] == 2
        assert stats["misses"] == 3
        assert abs(stats["hit_rate"] - 0.4) < 0.001

    @pytest.mark.asyncio
    async def test_stats_size_tracking(
        self, cache: VectorSearchCache
    ) -> None:
        """Test that cache size is tracked."""
        await cache.set("k1", [])
        await cache.set("k2", [])
        await cache.set("k3", [])

        stats = cache.get_stats()

        assert stats["size"] == 3
        assert stats["max_size"] == 5

    @pytest.mark.asyncio
    async def test_clear_resets_stats(self, cache: VectorSearchCache) -> None:
        """Test that clear resets statistics."""
        await cache.get("miss")
        await cache.set("hit", [])
        await cache.get("hit")

        await cache.clear()

        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["size"] == 0


# ==============================================================================
# Embedding Key Tests
# ==============================================================================


class TestEmbeddingKey:
    """Tests for embedding-based cache operations."""

    @pytest.mark.asyncio
    async def test_get_by_embedding_miss(
        self, cache: VectorSearchCache
    ) -> None:
        """Test get_by_embedding with cache miss."""
        embedding = [0.1, 0.2, 0.3]
        result = await cache.get_by_embedding(embedding)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_embedding_hit(
        self, cache: VectorSearchCache, sample_results
    ) -> None:
        """Test get_by_embedding with cache hit."""
        embedding = [0.1, 0.2, 0.3]

        await cache.set_by_embedding(embedding, sample_results)
        result = await cache.get_by_embedding(embedding)

        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_embedding_key_includes_limit(
        self, cache: VectorSearchCache
    ) -> None:
        """Test that embedding cache key includes limit parameter."""
        embedding = [0.1, 0.2, 0.3]
        results1 = [
            ContentRef(id="r1", source_type=ContentType.MARKDOWN, storage_backend=StorageBackend.OBSIDIAN)
        ]
        results2 = [
            ContentRef(id="r1", source_type=ContentType.MARKDOWN, storage_backend=StorageBackend.OBSIDIAN),
            ContentRef(id="r2", source_type=ContentType.MARKDOWN, storage_backend=StorageBackend.OBSIDIAN),
        ]

        # Set with different limits
        await cache.set_by_embedding(embedding, results1, limit=1)
        await cache.set_by_embedding(embedding, results2, limit=2)

        # Should retrieve correct results for each limit
        r1 = await cache.get_by_embedding(embedding, limit=1)
        r2 = await cache.get_by_embedding(embedding, limit=2)

        assert len(r1) == 1
        assert len(r2) == 2

    @pytest.mark.asyncio
    async def test_embedding_key_includes_source_ids(
        self, cache: VectorSearchCache
    ) -> None:
        """Test that embedding cache key includes source_ids filter."""
        embedding = [0.5, 0.6]
        results_a = [ContentRef(id="a", source_type=ContentType.MARKDOWN, storage_backend=StorageBackend.OBSIDIAN)]
        results_b = [ContentRef(id="b", source_type=ContentType.MARKDOWN, storage_backend=StorageBackend.OBSIDIAN)]

        await cache.set_by_embedding(embedding, results_a, source_ids=["source-a"])
        await cache.set_by_embedding(embedding, results_b, source_ids=["source-b"])

        r_a = await cache.get_by_embedding(embedding, source_ids=["source-a"])
        r_b = await cache.get_by_embedding(embedding, source_ids=["source-b"])

        assert len(r_a) == 1
        assert len(r_b) == 1


# ==============================================================================
# Global Cache Tests
# ==============================================================================


class TestGlobalCache:
    """Tests for global cache singleton."""

    def test_get_global_cache_returns_instance(self) -> None:
        """Test that get_global_cache returns VectorSearchCache."""
        cache = get_global_cache()
        assert isinstance(cache, VectorSearchCache)

    def test_get_global_cache_returns_same_instance(self) -> None:
        """Test that get_global_cache returns same instance."""
        cache1 = get_global_cache()
        cache2 = get_global_cache()
        assert cache1 is cache2  # Same instance (singleton)
