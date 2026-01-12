"""
API Models

Pydantic models for API requests and responses.
Single Responsibility: Only defines data structures.
"""

from typing import List, Optional

from pydantic import BaseModel


class SearchRequest(BaseModel):
    """Search request model."""

    query: str
    include_context: bool = True
    skip_cache: bool = False


class SearchResult(BaseModel):
    """Search result model."""

    question: str
    answer: str
    confidence: float
    sources: List[str]
    context: Optional[List[dict]] = None
    cached: bool = False


class ExportRequest(BaseModel):
    """Export request model for JSON/Markdown output."""

    query: str
    skip_cache: bool = False
    include_context: bool = True
