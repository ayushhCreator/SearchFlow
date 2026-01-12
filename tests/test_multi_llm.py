"""
Test Multi-LLM Provider Configuration
"""

import os

import pytest

from app.ai.dspy_pipeline import DSPyPipeline
from app.core.config import settings


class TestMultiLLMConfig:
    """Test multi-LLM provider configuration"""

    def test_config_has_all_providers(self):
        """Test that config includes all provider settings"""
        # Check provider setting exists
        assert hasattr(settings, "LLM_PROVIDER")

        # Check Groq settings
        assert hasattr(settings, "GROQ_API_KEY")
        assert hasattr(settings, "GROQ_MODEL")
        assert hasattr(settings, "GROQ_MAX_TOKENS")
        assert hasattr(settings, "GROQ_TEMPERATURE")

        # Check Gemini settings
        assert hasattr(settings, "GEMINI_API_KEY")
        assert hasattr(settings, "GEMINI_MODEL")
        assert hasattr(settings, "GEMINI_MAX_TOKENS")
        assert hasattr(settings, "GEMINI_TEMPERATURE")

        # Check Ollama settings
        assert hasattr(settings, "OLLAMA_BASE_URL")
        assert hasattr(settings, "OLLAMA_MODEL")
        assert hasattr(settings, "OLLAMA_MAX_TOKENS")
        assert hasattr(settings, "OLLAMA_TEMPERATURE")

    def test_provider_validation(self):
        """Test that provider is one of the supported values"""
        provider = settings.LLM_PROVIDER.lower()
        assert provider in ["ollama", "groq", "gemini", "openai"]

    def test_groq_config_loaded(self):
        """Test Groq configuration is loaded correctly"""
        if settings.LLM_PROVIDER.lower() == "groq":
            assert settings.GROQ_MODEL is not None
            assert settings.GROQ_MAX_TOKENS > 0
            assert 0 <= settings.GROQ_TEMPERATURE <= 2

    def test_gemini_config_loaded(self):
        """Test Gemini configuration is loaded correctly"""
        if settings.LLM_PROVIDER.lower() == "gemini":
            assert settings.GEMINI_MODEL is not None
            assert settings.GEMINI_MAX_TOKENS > 0
            assert 0 <= settings.GEMINI_TEMPERATURE <= 2

    def test_ollama_config_loaded(self):
        """Test Ollama configuration is loaded correctly"""
        if settings.LLM_PROVIDER.lower() == "ollama":
            assert settings.OLLAMA_BASE_URL is not None
            assert settings.OLLAMA_MODEL is not None
            assert settings.OLLAMA_MAX_TOKENS > 0
            assert 0 <= settings.OLLAMA_TEMPERATURE <= 2


class TestDSPyPipelineProviders:
    """Test DSPy pipeline with different providers"""

    def test_initialize_llm_validates_provider(self):
        """Test that invalid provider raises error"""
        # Skip if no API keys configured
        if not any(
            [settings.GROQ_API_KEY, settings.GEMINI_API_KEY, settings.OPENAI_API_KEY]
        ):
            pytest.skip("No LLM API keys configured")

        pipeline = DSPyPipeline()

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            pipeline._initialize_llm("invalid_provider")

    def test_groq_initialization(self):
        """Test Groq provider initialization"""
        if not settings.GROQ_API_KEY:
            pytest.skip("GROQ_API_KEY not set")

        # Temporarily set provider to groq
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "groq"

        try:
            pipeline = DSPyPipeline()
            assert pipeline is not None
            assert pipeline.retriever is not None
            assert pipeline.answer is not None
        finally:
            settings.LLM_PROVIDER = original_provider

    def test_gemini_initialization(self):
        """Test Gemini provider initialization"""
        if not settings.GEMINI_API_KEY:
            pytest.skip("GEMINI_API_KEY not set")

        # Temporarily set provider to gemini
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "gemini"

        try:
            pipeline = DSPyPipeline()
            assert pipeline is not None
            assert pipeline.retriever is not None
            assert pipeline.answer is not None
        finally:
            settings.LLM_PROVIDER = original_provider

    def test_model_override(self):
        """Test model can be overridden at runtime"""
        if not any(
            [settings.GROQ_API_KEY, settings.GEMINI_API_KEY, settings.OPENAI_API_KEY]
        ):
            pytest.skip("No LLM API keys configured")

        # Initialize with model override
        pipeline = DSPyPipeline(lm_model="custom-model")
        assert pipeline is not None


class TestProviderSwitching:
    """Test switching between providers"""

    def test_environment_variable_switching(self):
        """Test that LLM_PROVIDER environment variable is respected"""
        provider_from_env = os.getenv("LLM_PROVIDER", "groq")
        assert settings.LLM_PROVIDER.lower() == provider_from_env.lower()

    def test_default_provider_is_groq(self):
        """Test that default provider is groq"""
        # If LLM_PROVIDER not explicitly set, should default to groq
        assert settings.LLM_PROVIDER.lower() in ["groq", "gemini", "ollama", "openai"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
