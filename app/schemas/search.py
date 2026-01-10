"""
Pydantic Data Models for Search API

This module defines request/response schemas with validation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequestSchema(BaseModel):
    """
    Schema for search API request

    Example:
        {
            "query": "Best FastAPI practices",
            "limit": 10,
            "language": "en"
        }
    """

    query: str = Field(
        ..., min_length=1, max_length=500, description="Search query string"
    )
    limit: Optional[int] = Field(
        10, ge=1, le=50, description="Maximum number of results (1-50)"
    )
    language: Optional[str] = Field(
        "en", description="Language code (e.g., 'en', 'fr')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Best FastAPI practices",
                "limit": 10,
                "language": "en",
            }
        }


class SearchResultSchema(BaseModel):
    """Schema for individual search result"""

    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    snippet: str = Field(..., description="Result snippet/summary")
    source: Optional[str] = Field(None, description="Search engine source")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "FastAPI Best Practices",
                "url": "https://example.com/fastapi-practices",
                "snippet": "Learn the best practices for building FastAPI applications...",
                "source": "Google",
            }
        }


class AIInsightSchema(BaseModel):
    """Schema for AI insights"""

    key_points: List[str] = Field(..., description="Main insights extracted")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    summary: str = Field(..., description="AI-generated summary")


class SearchResponseSchema(BaseModel):
    """Complete response schema"""

    query: str = Field(..., description="Original query")
    results_count: int = Field(..., description="Number of results")
    results: List[SearchResultSchema] = Field(..., description="Search results")

    # AI processed output
    markdown_summary: str = Field(..., description="Human-readable markdown")
    json_data: dict = Field(..., description="Structured JSON data")
    insights: Optional[AIInsightSchema] = Field(None, description="AI insights")

    # Metadata
    processing_time: float = Field(..., description="Time to process (seconds)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Best FastAPI practices",
                "results_count": 10,
                "results": [
                    {
                        "title": "FastAPI Documentation",
                        "url": "https://fastapi.tiangolo.com",
                        "snippet": "Official FastAPI documentation...",
                        "source": "Google",
                    }
                ],
                "markdown_summary": (
                    "# FastAPI Best Practices\n\n## Key Points\n1. Use async endpoints..."
                ),
                "json_data": {
                    "practices": ["Use async", "Validate inputs", "Use dependencies"]
                },
                "insights": {
                    "key_points": ["Use async endpoints", "Proper validation"],
                    "confidence": 0.95,
                    "summary": "FastAPI follows async-first design...",
                },
                "processing_time": 2.5,
                "timestamp": "2024-01-10T10:30:00",
            }
        }
