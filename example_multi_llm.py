#!/usr/bin/env python3
"""
Example: Using SearchFlow with Multiple LLM Providers

This script demonstrates how to use SearchFlow with different LLM providers.
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ai.dspy_pipeline import DSPyPipeline  # noqa: E402
from app.core.config import settings  # noqa: E402


def main():
    """Demonstrate multi-provider usage"""

    print("=" * 60)
    print("SearchFlow Multi-LLM Provider Demo")
    print("=" * 60)
    print()

    # Show current configuration
    print("📋 Current Configuration:")
    print(f"   Provider: {settings.LLM_PROVIDER}")
    print(f"   SearXNG: {settings.SEARXNG_URL}")

    if settings.LLM_PROVIDER.lower() == "groq":
        print(f"   Model: {settings.GROQ_MODEL}")
        print(f"   Max Tokens: {settings.GROQ_MAX_TOKENS}")
    elif settings.LLM_PROVIDER.lower() == "gemini":
        print(f"   Model: {settings.GEMINI_MODEL}")
        print(f"   Max Tokens: {settings.GEMINI_MAX_TOKENS}")
    elif settings.LLM_PROVIDER.lower() == "ollama":
        print(f"   Model: {settings.OLLAMA_MODEL}")
        print(f"   Base URL: {settings.OLLAMA_BASE_URL}")
    elif settings.LLM_PROVIDER.lower() == "openai":
        print(f"   Model: {settings.OPENAI_MODEL}")

    print()
    print("=" * 60)
    print()

    # Initialize pipeline
    try:
        print("🔄 Initializing DSPy pipeline...")
        pipeline = DSPyPipeline(k_results=3)
        print("✅ Pipeline initialized successfully!")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        print()
        print("💡 Tips:")
        print("   - Make sure your API key is set in .env")
        print("   - For Ollama, ensure 'ollama serve' is running")
        print("   - For SearXNG, run 'make docker-up'")
        return 1

    # Example query
    query = "What is Python programming language?"

    print(f"🔍 Searching: {query}")
    print()

    try:
        # Perform search and answer
        result = pipeline.search_and_answer(query)

        # Display results
        print("=" * 60)
        print("📊 Results:")
        print("=" * 60)
        print()
        print(f"❓ Question: {result['question']}")
        print()
        print(f"💡 Answer: {result['answer']}")
        print()
        print(f"🎯 Confidence: {result['confidence']:.2%}")
        print()

        if result.get("sources"):
            print("🔗 Sources:")
            for i, source in enumerate(result["sources"][:3], 1):
                print(f"   {i}. {source}")

        print()
        print("=" * 60)
        print()
        print("✅ Search completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Search failed: {e}")
        print()
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
