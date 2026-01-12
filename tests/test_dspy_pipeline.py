"""
DSPy Pipeline Tests
"""

import os

import pytest

from app.ai.dspy_pipeline import DSPyPipeline


@pytest.mark.asyncio
class TestDSPyPipeline:
    """Test DSPy + SearXNG integration"""

    def test_pipeline_initialization(self):
        """Test DSPy pipeline can be initialized"""
        # Skip if no OpenAI key
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        pipeline = DSPyPipeline()
        assert pipeline is not None
        assert pipeline.retriever is not None

    def test_search_and_answer(self):
        """Test search and answer functionality"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        pipeline = DSPyPipeline()
        result = pipeline.search_and_answer("What is Python?")

        assert result["question"] == "What is Python?"
        assert result["answer"] is not None
        assert result["confidence"] >= 0
        assert result["confidence"] <= 1
