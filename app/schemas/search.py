"""
Pydantic Data Models

This module defines request/response schemas for API endpoints.
"""

from typing import List, Optional

from pydantic import BaseModel


class SearchRequestSchema(BaseModel):
    """Schema for search API request"""

    query: str
    limit: Optional[int] = 10

    class Config:
        json_schema_extra = {
            "example": {"query": "Best FastAPI practices", "limit": 10}
        }


class SearchResultSchema(BaseModel):
    """Schema for individual search result"""

    title: str
    url: str
    snippet: str


class SearchResponseSchema(BaseModel):
    """Schema for search API response"""

    query: str
    results: List[SearchResultSchema]
    markdown_summary: str
    json_data: dict
