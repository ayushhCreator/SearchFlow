"""
Configuration Management

This module manages all application configuration from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    API_TITLE: str = "SearchFlow"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # CORS Configuration
    ALLOWED_ORIGINS: list = ["http://localhost", "http://localhost:3000"]

    # Search Configuration
    SEARXNG_URL: str = "http://localhost:8888"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


# Create settings instance
settings = Settings()
