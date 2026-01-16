"""
LLM Provider Configuration

Configures language models for different providers.
Single Responsibility: Only handles LLM initialization.
Open/Closed: Easy to add new providers without modifying existing code.
"""

import logging
from typing import Optional

import dspy

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_llm(
    provider: Optional[str] = None,
    model_override: Optional[str] = None,
) -> dspy.LM:
    """
    Create LLM instance based on provider.

    Args:
        provider: LLM provider ("gemini", "groq", "ollama", "openai")
        model_override: Optional model name override

    Returns:
        Configured DSPy LLM instance

    Raises:
        ValueError: If provider is unknown or API key missing
    """
    provider = (provider or settings.LLM_PROVIDER).lower()
    logger.info(f"🤖 Creating LLM | Provider: {provider.upper()}")

    if provider == "gemini":
        return _create_gemini_lm(model_override)
    elif provider == "groq":
        return _create_groq_lm(model_override)
    elif provider == "ollama":
        return _create_ollama_lm(model_override)
    elif provider == "openai":
        return _create_openai_lm(model_override)
    elif provider == "openrouter":
        return _create_openrouter_lm(model_override)
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported: 'gemini', 'groq', 'ollama', 'openai', 'openrouter'"
        )


def _create_gemini_lm(model_override: Optional[str] = None) -> dspy.LM:
    """Create Gemini LLM."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment")

    model = model_override or settings.GEMINI_MODEL
    logger.info(f"Using Gemini model: {model}")

    return dspy.LM(
        model=f"gemini/{model}",
        api_key=api_key,
        max_tokens=settings.GEMINI_MAX_TOKENS,
        temperature=settings.GEMINI_TEMPERATURE,
    )


def _create_groq_lm(model_override: Optional[str] = None) -> dspy.LM:
    """Create Groq LLM."""
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")

    model = model_override or settings.GROQ_MODEL
    logger.info(f"Using Groq model: {model}")

    return dspy.LM(
        model=f"groq/{model}",
        api_key=api_key,
        max_tokens=settings.GROQ_MAX_TOKENS,
        temperature=settings.GROQ_TEMPERATURE,
    )


def _create_ollama_lm(model_override: Optional[str] = None) -> dspy.LM:
    """Create Ollama LLM."""
    model = model_override or settings.OLLAMA_MODEL
    logger.info(f"Using Ollama model: {model} at {settings.OLLAMA_BASE_URL}")

    return dspy.LM(
        model=f"ollama/{model}",
        api_base=settings.OLLAMA_BASE_URL,
        max_tokens=settings.OLLAMA_MAX_TOKENS,
        temperature=settings.OLLAMA_TEMPERATURE,
    )


def _create_openai_lm(model_override: Optional[str] = None) -> dspy.LM:
    """Create OpenAI LLM."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    model = model_override or settings.OPENAI_MODEL
    logger.info(f"Using OpenAI model: {model}")

    return dspy.LM(model=f"openai/{model}", api_key=api_key, max_tokens=1000)


def _create_openrouter_lm(model_override: Optional[str] = None) -> dspy.LM:
    """Create OpenRouter LLM."""
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in environment")

    model = model_override or settings.OPENROUTER_MODEL
    logger.info(f"Using OpenRouter model: {model}")

    return dspy.LM(
        model=f"openai/{model}",
        api_key=api_key,
        api_base="https://openrouter.ai/api/v1",
        max_tokens=settings.OPENROUTER_MAX_TOKENS,
        temperature=settings.OPENROUTER_TEMPERATURE,
    )
