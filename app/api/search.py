"""
Search API Routes

This module defines the search endpoints using DSPy + SearXNG.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ai.dspy_pipeline import DSPyPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


class SearchRequest(BaseModel):
    """Search request model"""

    query: str
    include_context: bool = True


class SearchResult(BaseModel):
    """Search result model"""

    question: str
    answer: str
    confidence: float
    sources: List[str]
    context: Optional[List[dict]] = None


@router.post("/search", response_model=SearchResult)
async def search(request: SearchRequest) -> SearchResult:
    """
    Search and answer using DSPy + SearXNG

    Example:
    ```bash
    curl -X POST http://localhost:8007/api/v1/search \
      -H "Content-Type: application/json" \
      -d '{"query": "what is dspy"}'
    ```
    """
    try:
        logger.info(f"Search request: {request.query}")

        # Initialize DSPy pipeline
        try:
            pipeline = DSPyPipeline(k_results=5)
        except ValueError as e:
            logger.error(f"DSPy initialization failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="Search service not configured. Please set OPENAI_API_KEY in .env file.",
            )

        # Search and answer
        result = pipeline.search_and_answer(request.query)

        # Format response
        response = SearchResult(
            question=result["question"],
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result["sources"],
            context=result["context"] if request.include_context else None,
        )

        return response

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/health")
async def search_health():
    """Health check for search functionality"""
    return {"status": "healthy", "searxng": "configured", "dspy": "ready"}
