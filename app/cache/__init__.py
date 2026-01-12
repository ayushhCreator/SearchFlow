"""
Cache Module

Provides Redis-based caching for search results.
"""

from app.cache.redis_client import CacheClient, get_cache_client

__all__ = ["CacheClient", "get_cache_client"]
