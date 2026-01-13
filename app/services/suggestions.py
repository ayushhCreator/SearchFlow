"""
Suggestions Service

Generates AI-powered search query suggestions:
- For new users: Based on trending tech topics from real-time search
- For returning users: Personalized based on search history
"""

import logging
from typing import List, Optional

import dspy
import httpx

from app.ai.signatures import SuggestionGenerator
from app.core.config import settings

logger = logging.getLogger("searchflow")


class SuggestionService:
    """Generate personalized search suggestions using AI."""

    def __init__(self):
        """Initialize the suggestion service with LLM."""
        self._lm = self._init_lm()
        self.generator = dspy.Predict(SuggestionGenerator)

    def _init_lm(self) -> dspy.LM:
        """Initialize the language model based on settings."""
        provider = settings.LLM_PROVIDER.lower()

        if provider == "groq":
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set")
            return dspy.LM(
                model=f"groq/{settings.GROQ_MODEL}",
                api_key=settings.GROQ_API_KEY,
                max_tokens=settings.GROQ_MAX_TOKENS,
                temperature=settings.GROQ_TEMPERATURE,
            )
        elif provider == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set")
            return dspy.LM(
                model=f"gemini/{settings.GEMINI_MODEL}",
                api_key=settings.GEMINI_API_KEY,
                max_tokens=settings.GEMINI_MAX_TOKENS,
                temperature=settings.GEMINI_TEMPERATURE,
            )
        elif provider == "ollama":
            return dspy.LM(
                model=f"ollama_chat/{settings.OLLAMA_MODEL}",
                api_base=settings.OLLAMA_BASE_URL,
                max_tokens=settings.OLLAMA_MAX_TOKENS,
                temperature=settings.OLLAMA_TEMPERATURE,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    async def _fetch_trending_topics(self) -> str:
        """Fetch trending tech topics using SearXNG."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{settings.SEARXNG_URL}/search",
                    params={
                        "q": "latest technology news trends 2024",
                        "format": "json",
                        "categories": "it,science",
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Extract titles from top results
                results = data.get("results", [])[:10]
                topics = [r.get("title", "") for r in results if r.get("title")]
                return (
                    "\n".join(topics[:8])
                    if topics
                    else "AI, machine learning, web development"
                )

        except Exception as e:
            logger.warning(f"Failed to fetch trending topics: {e}")
            return "AI developments, web frameworks, cloud computing, cybersecurity, data science"

    def generate_suggestions(
        self,
        history: Optional[List[str]] = None,
    ) -> List[str]:
        """Generate search suggestions synchronously."""
        try:
            user_type = "returning" if history and len(history) > 0 else "new"
            context = "\n".join(history[:10]) if history else ""

            with dspy.context(lm=self._lm):
                result = self.generator(context=context, user_type=user_type)

            # Parse suggestions (one per line)
            suggestions = [
                line.strip()
                for line in result.suggestions.strip().split("\n")
                if line.strip() and len(line.strip()) > 5
            ]

            return suggestions[:5] if suggestions else self._fallback_suggestions()

        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return self._fallback_suggestions()

    async def generate_suggestions_async(
        self,
        history: Optional[List[str]] = None,
    ) -> List[str]:
        """Generate search suggestions with real-time trending topics for new users."""
        try:
            user_type = "returning" if history and len(history) > 0 else "new"

            # For new users, fetch trending topics
            if user_type == "new":
                context = await self._fetch_trending_topics()
            else:
                context = "\n".join(history[:10]) if history else ""

            with dspy.context(lm=self._lm):
                result = self.generator(context=context, user_type=user_type)

            # Parse suggestions (one per line)
            suggestions = [
                line.strip()
                for line in result.suggestions.strip().split("\n")
                if line.strip() and len(line.strip()) > 5
            ]

            return suggestions[:5] if suggestions else self._fallback_suggestions()

        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return self._fallback_suggestions()

    def _fallback_suggestions(self) -> List[str]:
        """Return fallback suggestions if AI fails."""
        return [
            "What are the latest features in Next.js?",
            "Explain quantum computing simply",
            "Best practices for React performance",
            "How does a transformer model work?",
            "Compare Python vs Rust for backend",
        ]


# Singleton instance
_suggestion_service: Optional[SuggestionService] = None


def get_suggestion_service() -> SuggestionService:
    """Get or create the suggestion service singleton."""
    global _suggestion_service
    if _suggestion_service is None:
        _suggestion_service = SuggestionService()
    return _suggestion_service
