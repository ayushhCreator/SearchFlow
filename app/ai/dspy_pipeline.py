"""
DSPy Processing Pipeline

Uses DSPy for AI reasoning over search results.
"""

import logging
from typing import Dict, List, Optional

import dspy

from app.core.config import settings
from app.search.dspy_retriever import SearXNGRetriever

logger = logging.getLogger(__name__)


# DSPy Signature: what the AI will be asked to do
class SearchQA(dspy.Signature):
    """Answer a question using web search context"""

    context = dspy.InputField(desc="Information from web search")
    question = dspy.InputField(desc="The user's question")
    answer = dspy.OutputField(desc="A comprehensive answer based on context")
    confidence = dspy.OutputField(desc="Confidence score 0-1")


class DSPyPipeline:
    """DSPy pipeline for search + reasoning"""

    def __init__(
        self,
        lm_model: Optional[str] = None,
        searx_url: Optional[str] = None,
        k_results: int = 5,
    ):
        """
        Initialize DSPy pipeline

        Args:
            lm_model: LLM model to use (default: from settings)
            searx_url: SearXNG URL (default: from settings)
            k_results: Number of search results to use
        """
        # Configure LLM based on provider
        provider = settings.LLM_PROVIDER.lower()
        logger.info(f"Initializing LLM provider: {provider}")

        lm = self._initialize_llm(provider, lm_model)
        dspy.settings.configure(lm=lm)

        # Configure retriever
        self.retriever = SearXNGRetriever(searx_url=searx_url, k=k_results)

        # Create reasoning module
        self.answer = dspy.ChainOfThought(SearchQA)

    def _initialize_llm(self, provider: str, model_override: Optional[str] = None):
        """
        Initialize LLM based on provider type

        Args:
            provider: LLM provider ("ollama", "groq", or "gemini")
            model_override: Optional model name override

        Returns:
            Configured DSPy LLM instance
        """
        if provider == "gemini":
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")

            model = model_override or settings.GEMINI_MODEL
            logger.info(f"Using Gemini model: {model}")

            # DSPy uses LiteLLM format: "gemini/model-name"
            return dspy.LM(
                model=f"gemini/{model}",
                api_key=api_key,
                max_tokens=settings.GEMINI_MAX_TOKENS,
                temperature=settings.GEMINI_TEMPERATURE,
            )

        elif provider == "groq":
            api_key = settings.GROQ_API_KEY
            if not api_key:
                raise ValueError("GROQ_API_KEY not set in environment")

            model = model_override or settings.GROQ_MODEL
            logger.info(f"Using Groq model: {model}")

            # DSPy uses LiteLLM format: "groq/model-name"
            return dspy.LM(
                model=f"groq/{model}",
                api_key=api_key,
                max_tokens=settings.GROQ_MAX_TOKENS,
                temperature=settings.GROQ_TEMPERATURE,
            )

        elif provider == "ollama":
            model = model_override or settings.OLLAMA_MODEL
            logger.info(f"Using Ollama model: {model} at {settings.OLLAMA_BASE_URL}")

            # DSPy uses LiteLLM format: "ollama/model-name"
            return dspy.LM(
                model=f"ollama/{model}",
                api_base=settings.OLLAMA_BASE_URL,
                max_tokens=settings.OLLAMA_MAX_TOKENS,
                temperature=settings.OLLAMA_TEMPERATURE,
            )

        elif provider == "openai":
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")

            model = model_override or settings.OPENAI_MODEL
            logger.info(f"Using OpenAI model: {model}")

            # DSPy uses LiteLLM format: "openai/model-name"
            return dspy.LM(model=f"openai/{model}", api_key=api_key, max_tokens=1000)

        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. "
                f"Supported: 'ollama', 'groq', 'gemini', 'openai'"
            )

    async def process_results(self, query: str, results: List[Dict]) -> Dict:
        """
        Process search results with AI reasoning (compatibility method)

        Args:
            query: Original search query
            results: Raw search results from SearXNG

        Returns:
            Structured data with insights
        """
        return self.search_and_answer(query)

    def search_and_answer(self, question: str) -> Dict:
        """
        Search the web and answer a question using DSPy

        Args:
            question: User's question

        Returns:
            Dictionary with answer, context, and confidence
        """
        try:
            logger.info(f"Processing question: {question}")

            # Step 1: Retrieve relevant passages
            passages = self.retriever(question)

            if not passages:
                return {
                    "question": question,
                    "answer": "Could not find relevant information",
                    "context": [],
                    "confidence": 0.0,
                    "sources": [],
                }

            # Step 2: Combine context (passages are now strings)
            context = "\n\n".join(passages)

            # Step 3: Use DSPy to reason and answer
            result = self.answer(
                context=context[:2000], question=question  # Limit context size
            )

            # Step 4: Extract confidence
            try:
                confidence = float(result.confidence.split()[0])
            except (ValueError, AttributeError, IndexError):
                confidence = 0.7

            # Step 5: Build response with metadata from retriever
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
                "confidence": confidence,
                "sources": [r.get("url", "") for r in raw_results if r.get("url")],
            }

        except Exception as e:
            logger.error(f"DSPy pipeline failed: {e}")
            return {
                "question": question,
                "answer": f"Error: {str(e)}",
                "context": [],
                "confidence": 0.0,
            }
