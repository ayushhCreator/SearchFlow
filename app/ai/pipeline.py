"""
DSPy Pipeline

Main search and reasoning pipeline.
Single Responsibility: Orchestrates search + AI reasoning.
"""

import logging
import time
from typing import Dict, List, Optional

import dspy

from app.ai.llm_providers import create_llm
from app.ai.signatures import SearchQA
from app.core.config import settings
from app.search.dspy_retriever import SearXNGRetriever

logger = logging.getLogger(__name__)


class DSPyPipeline:
    """
    DSPy pipeline for search + reasoning.

    Thread-safe: Uses dspy.context() for concurrent requests.
    """

    def __init__(
        self,
        lm_model: Optional[str] = None,
        searx_url: Optional[str] = None,
        k_results: int = 5,
    ):
        """Initialize DSPy pipeline."""
        self._provider = settings.LLM_PROVIDER.lower()
        self._lm = create_llm(self._provider, lm_model)
        self._model_name = getattr(self._lm, "model", "unknown")

        logger.info(f"✅ LLM Ready | Model: {self._model_name}")

        self.retriever = SearXNGRetriever(searx_url=searx_url, k=k_results)
        logger.info(f"🔍 Retriever configured | k={k_results}")

        self.answer = dspy.ChainOfThought(SearchQA)

    async def process_results(self, query: str, results: List[Dict]) -> Dict:
        """Process search results (compatibility method)."""
        return self.search_and_answer(query)

    def search_and_answer(self, question: str) -> Dict:
        """Search the web and answer using DSPy."""
        try:
            logger.info(f"📝 Processing question: {question[:80]}...")

            start_retrieval = time.time()
            passages = self.retriever(question)
            retrieval_time = time.time() - start_retrieval
            logger.info(
                f"🔍 Retrieved {len(passages)} passages in {retrieval_time:.2f}s"
            )

            if not passages:
                return self._empty_result(question)

            context = "\n\n".join(passages)

            logger.info(
                f"🧠 Calling LLM | Provider: {self._provider.upper()} | "
                f"Model: {self._model_name}"
            )
            start_llm = time.time()

            with dspy.context(lm=self._lm):
                result = self.answer(context=context[:2000], question=question)

            llm_time = time.time() - start_llm
            logger.info(f"✅ LLM responded in {llm_time:.2f}s")

            return self._build_response(question, result, passages)

        except Exception as e:
            logger.error(f"DSPy pipeline failed: {e}")
            return {
                "question": question,
                "answer": f"Error: {str(e)}",
                "context": [],
                "confidence": 0.0,
            }

    def _empty_result(self, question: str) -> Dict:
        """Return empty result when no passages found."""
        return {
            "question": question,
            "answer": "Could not find relevant information",
            "context": [],
            "confidence": 0.0,
            "sources": [],
        }

    def _extract_confidence(self, result) -> float:
        """Extract confidence score from result."""
        try:
            return float(result.confidence.split()[0])
        except (ValueError, AttributeError, IndexError):
            return 0.7

    def _build_response(self, question: str, result, passages: List[str]) -> Dict:
        """Build response dict from result."""
        raw_results = getattr(self.retriever, "_last_results", [])

        return {
            "question": question,
            "answer": result.answer,
            "context": [
                {
                    "text": passages[i][:500] if i < len(passages) else "",
                    "url": raw_results[i].get("url", "")
                    if i < len(raw_results)
                    else "",
                    "source": raw_results[i].get("engine", "searxng")
                    if i < len(raw_results)
                    else "",
                    "title": raw_results[i].get("title", "")
                    if i < len(raw_results)
                    else "",
                }
                for i in range(len(passages))
            ],
            "confidence": self._extract_confidence(result),
            "sources": [r.get("url", "") for r in raw_results if r.get("url")],
        }
