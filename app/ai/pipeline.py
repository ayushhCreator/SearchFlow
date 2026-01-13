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
from app.ai.signatures import ContextRanker, QueryDecomposer, SearchQA
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
        k_results: int = 10,  # Increased for reranking
    ):
        """Initialize DSPy pipeline."""
        self._provider = settings.LLM_PROVIDER.lower()
        self._lm = create_llm(self._provider, lm_model)
        self._model_name = getattr(self._lm, "model", "unknown")

        logger.info(f"✅ LLM Ready | Model: {self._model_name}")

        self.retriever = SearXNGRetriever(searx_url=searx_url, k=k_results)
        logger.info(f"🔍 Retriever configured | k={k_results}")

        self.answer = dspy.ChainOfThought(SearchQA)
        self.ranker = dspy.ChainOfThought(ContextRanker)
        self.decomposer = dspy.ChainOfThought(QueryDecomposer)

    async def process_results(self, query: str, results: List[Dict]) -> Dict:
        """Process search results (compatibility method)."""
        return self.search_and_answer(query)

    def search_and_answer(self, question: str) -> Dict:
        """Search the web and answer using DSPy."""
        try:
            logger.info(f"📝 Processing question: {question[:80]}...")

            # Step 1: Retrieval
            start_retrieval = time.time()
            passages = self.retriever(question)
            retrieval_time = time.time() - start_retrieval
            logger.info(
                f"🔍 Retrieved {len(passages)} passages in {retrieval_time:.2f}s"
            )

            if not passages:
                return self._empty_result(question)

            # Step 2: Reranking
            logger.info("⚖️ Reranking passages...")
            start_rerank = time.time()
            selected_indices = self._rerank_passages(question, passages)
            rerank_time = time.time() - start_rerank
            logger.info(
                f"✅ Selected {len(selected_indices)}/{len(passages)} passages "
                f"in {rerank_time:.2f}s"
            )

            # Step 3: Synthesis with numbered passages for citations
            ranked_passages = [passages[i] for i in selected_indices]
            # Format with citation markers: [0], [1], etc.
            numbered_context = "\n\n".join(
                [f"[{idx}] {p}" for idx, p in enumerate(ranked_passages)]
            )

            logger.info(
                f"🧠 Calling LLM | Provider: {self._provider.upper()} | "
                f"Model: {self._model_name}"
            )
            start_llm = time.time()

            with dspy.context(lm=self._lm):
                result = self.answer(context=numbered_context[:3000], question=question)

            llm_time = time.time() - start_llm
            logger.info(f"✅ LLM responded in {llm_time:.2f}s")

            return self._build_response(question, result, selected_indices)

        except Exception as e:
            logger.error(f"DSPy pipeline failed: {e}")
            return {
                "question": question,
                "answer": f"Error: {str(e)}",
                "context": [],
                "confidence": 0.0,
            }

    def _rerank_passages(self, question: str, passages: List[str]) -> List[int]:
        """Rerank passages factoring in both relevance and credibility."""
        if not passages:
            return []

        raw_results = getattr(self.retriever, "_last_results", [])

        # Format context for ranking (index + credibility + preview)
        context_lines = []
        for i, p in enumerate(passages):
            cred = (
                raw_results[i].get("credibility_score", 0.5)
                if i < len(raw_results)
                else 0.5
            )
            context_lines.append(f"[{i}] (credibility: {cred:.2f}) {p[:180]}...")
        context_str = "\n".join(context_lines)

        try:
            with dspy.context(lm=self._lm):
                result = self.ranker(query=question, context=context_str)

            indices_str = result.selected_indices
            # Parse indices: "1, 3, 5" -> [1, 3, 5]
            indices = [
                int(i.strip())
                for i in indices_str.replace(".", ",").split(",")
                if i.strip().isdigit()
            ]

            # Filter valid indices
            valid_indices = [i for i in indices if 0 <= i < len(passages)]

            if not valid_indices:
                logger.warning(
                    "Reranker returned no valid indices, using top by credibility"
                )
                # Fallback: sort by credibility and take top 3
                sorted_by_cred = sorted(
                    range(len(raw_results)),
                    key=lambda x: raw_results[x].get("credibility_score", 0.5),
                    reverse=True,
                )
                return sorted_by_cred[:3]

            # Limit to top 5 relevant to avoid context overflow
            return valid_indices[:5]

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return list(range(min(5, len(passages))))  # Fallback to top 5

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

    def _build_response(self, question: str, result, indices: List[int]) -> Dict:
        """Build response dict using selected indices."""
        raw_results = getattr(self.retriever, "_last_results", [])

        context_objects = []
        for i in indices:
            if i < len(raw_results):
                raw = raw_results[i]
                context_objects.append(
                    {
                        "text": raw.get("content", "")[:500],
                        "url": raw.get("url", ""),
                        "source": raw.get("engine", "searxng"),
                        "title": raw.get("title", ""),
                        "credibility_score": raw.get("credibility_score", 0.5),
                        "credibility_category": raw.get(
                            "credibility_category", "general"
                        ),
                    }
                )

        return {
            "question": question,
            "answer": result.answer,
            "context": context_objects,
            "confidence": self._extract_confidence(result),
            "sources": [c["url"] for c in context_objects if c["url"]],
        }

    def _is_complex_query(self, query: str) -> bool:
        """Check if query is complex enough to warrant decomposition."""
        complex_indicators = [
            "compare",
            "vs",
            "versus",
            "difference between",
            "pros and cons",
            "advantages and disadvantages",
            "how does",
            "why does",
            "explain the relationship",
            "what are the",
            " and ",
            "best practices for",
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in complex_indicators)

    def _decompose_query(self, query: str) -> List[str]:
        """Decompose complex query into sub-queries."""
        try:
            with dspy.context(lm=self._lm):
                result = self.decomposer(query=query)

            # Parse sub-queries (newline-separated)
            sub_queries = [
                q.strip()
                for q in result.sub_queries.split("\n")
                if q.strip() and len(q.strip()) > 5
            ]

            # Limit to 4 sub-queries max
            return sub_queries[:4] if sub_queries else [query]

        except Exception as e:
            logger.error(f"Query decomposition failed: {e}")
            return [query]

    def complex_search(self, question: str) -> Dict:
        """
        Search with automatic query decomposition for complex questions.

        Breaks complex queries into sub-queries, searches each,
        then synthesizes a comprehensive answer.
        """
        if not self._is_complex_query(question):
            return self.search_and_answer(question)

        logger.info(f"🔀 Complex query detected, decomposing: {question[:50]}...")
        sub_queries = self._decompose_query(question)
        logger.info(f"📋 Decomposed into {len(sub_queries)} sub-queries")

        # Collect passages from all sub-queries
        all_passages = []
        all_raw_results = []

        for sq in sub_queries:
            logger.info(f"🔍 Sub-query: {sq}")
            passages = self.retriever(sq)
            all_passages.extend(passages)
            all_raw_results.extend(getattr(self.retriever, "_last_results", []))

        # Deduplicate by URL
        seen_urls = set()
        unique_raw = []
        unique_passages = []
        for raw, passage in zip(all_raw_results, all_passages):
            url = raw.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_raw.append(raw)
                unique_passages.append(passage)

        # Store for reranking
        self.retriever._last_results = unique_raw[:15]

        if not unique_passages:
            return self._empty_result(question)

        # Rerank combined results
        selected_indices = self._rerank_passages(question, unique_passages[:15])

        # Synthesize
        ranked_passages = [unique_passages[i] for i in selected_indices]
        numbered_context = "\n\n".join(
            [f"[{idx}] {p}" for idx, p in enumerate(ranked_passages)]
        )

        with dspy.context(lm=self._lm):
            result = self.answer(context=numbered_context[:3500], question=question)

        return self._build_response(question, result, selected_indices)
