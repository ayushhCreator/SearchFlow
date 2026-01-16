"""
Configuration Management

This module manages all application configuration from environment variables.
"""

from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    API_TITLE: str = "SearchFlow"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # CORS Configuration
    ALLOWED_ORIGINS: Union[
        List[str], str
    ] = "http://localhost,http://localhost:3000,http://localhost:8007"

    # Search Configuration
    SEARXNG_URL: str = "http://localhost:8888"
    SEARXNG_SECRET: Optional[str] = None
    SEARXNG_ENGINES: Optional[str] = None

    # Cache Configuration (Redis)
    # Default: 6380 (Docker). If reusing Frappe's Redis, use port 13000
    REDIS_URL: str = "redis://localhost:6380"
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour in seconds
    CACHE_PREFIX: str = "searchflow:"

    # LLM Configuration (for DSPy)
    LLM_PROVIDER: str = "openrouter"  # "ollama", "groq", "gemini", "openai", or "openrouter"

    # Gemini Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash-lite"
    GEMINI_MAX_TOKENS: int = 1000
    GEMINI_TEMPERATURE: float = 0.3

    # Groq Configuration
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_MAX_TOKENS: int = 500
    GROQ_TEMPERATURE: float = 0.3

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    OLLAMA_MAX_TOKENS: int = 1000
    OLLAMA_TEMPERATURE: float = 0.3

    # Legacy OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # OpenRouter Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "nvidia/nemotron-nano-12b-v2-vl:free"
    OPENROUTER_MAX_TOKENS: int = 5000
    OPENROUTER_TEMPERATURE: float = 0.3

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Parse ALLOWED_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()
