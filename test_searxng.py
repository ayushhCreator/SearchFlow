#!/usr/bin/env python3
"""
Quick test script to verify SearXNG is working
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.search.searxng_client import SearXNGClient  # noqa: E402


async def test_searxng():
    """Test SearXNG connection and search"""
    print("🔍 Testing SearXNG connection...")

    try:
        async with SearXNGClient() as client:
            # Test search
            results = await client.search("python programming", limit=3)

            print(f"✅ Found {len(results)} results")

            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   Source: {result['source']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure SearXNG is running: make docker-up")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_searxng())
    sys.exit(0 if success else 1)
