"""
Redis Cache Client

Provides caching functionality for search results using Redis.
Reduces LLM API costs and improves response times for repeated queries.
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global cache client instance
_cache_client: Optional["CacheClient"] = None


class CacheClient:
    """
    Redis-based cache client for storing search results.

    Features:
    - Hash-based key generation for queries
    - TTL-based expiration
    - JSON serialization for complex data
    - Graceful fallback if Redis unavailable
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache client.

        Args:
            redis_url: Redis connection URL (defaults to settings)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.prefix = settings.CACHE_PREFIX
        self.ttl = settings.CACHE_TTL
        self.enabled = settings.CACHE_ENABLED
        self._redis: Optional[redis.Redis] = None
        self._connected = False

    async def connect(self) -> bool:
        """
        Connect to Redis.

        Returns:
            True if connected successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Cache is disabled")
            return False

        try:
            self._redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self._redis.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {self.redis_url}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._connected = False
            logger.info("Disconnected from Redis")

    def _generate_key(self, query: str) -> str:
        """
        Generate cache key from query.

        Uses SHA-256 hash of normalized query for consistent keys.

        Args:
            query: Search query string

        Returns:
            Cache key string
        """
        # Normalize query: lowercase, strip whitespace
        normalized = query.lower().strip()
        # Generate hash
        query_hash = hashlib.sha256(normalized.encode()).hexdigest()[:16]
        return f"{self.prefix}query:{query_hash}"

    async def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result for query.

        Args:
            query: Search query string

        Returns:
            Cached result dict or None if not found
        """
        if not self._connected or not self._redis:
            return None

        try:
            key = self._generate_key(query)
            cached = await self._redis.get(key)

            if cached:
                logger.info(f"Cache HIT for query: {query[:50]}...")
                return json.loads(cached)
            else:
                logger.debug(f"Cache MISS for query: {query[:50]}...")
                return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, query: str, result: Dict[str, Any]) -> bool:
        """
        Store result in cache.

        Args:
            query: Search query string
            result: Result dict to cache

        Returns:
            True if stored successfully, False otherwise
        """
        if not self._connected or not self._redis:
            return False

        try:
            key = self._generate_key(query)
            # Add cache metadata
            result_with_meta = {
                **result,
                "_cached": True,
                "_cache_key": key,
            }
            await self._redis.setex(
                key,
                self.ttl,
                json.dumps(result_with_meta),
            )
            logger.info(f"Cached result for query: {query[:50]}... (TTL: {self.ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, query: str) -> bool:
        """
        Delete cached result for query.

        Args:
            query: Search query string

        Returns:
            True if deleted, False otherwise
        """
        if not self._connected or not self._redis:
            return False

        try:
            key = self._generate_key(query)
            await self._redis.delete(key)
            logger.info(f"Deleted cache for query: {query[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def clear_all(self) -> int:
        """
        Clear all cached results.

        Returns:
            Number of keys deleted
        """
        if not self._connected or not self._redis:
            return 0

        try:
            pattern = f"{self.prefix}*"
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self._redis.delete(*keys)
                logger.info(f"Cleared {deleted} cached entries")
                return deleted
            return 0

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        if not self._connected or not self._redis:
            return {"connected": False, "enabled": self.enabled}

        try:
            info = await self._redis.info("memory")
            db_size = await self._redis.dbsize()

            return {
                "connected": True,
                "enabled": self.enabled,
                "total_keys": db_size,
                "memory_used": info.get("used_memory_human", "N/A"),
                "ttl_seconds": self.ttl,
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"connected": False, "error": str(e)}


async def get_cache_client() -> CacheClient:
    """
    Get or create global cache client.

    Returns:
        CacheClient instance
    """
    global _cache_client

    if _cache_client is None:
        _cache_client = CacheClient()
        await _cache_client.connect()

    return _cache_client


async def close_cache_client() -> None:
    """Close global cache client."""
    global _cache_client

    if _cache_client:
        await _cache_client.disconnect()
        _cache_client = None
