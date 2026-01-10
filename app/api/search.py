"""
Search API Routes

This module defines the search endpoints.
"""

import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.ai.dspy_pipeline import DSPyPipeline
from app.schemas.search import (
    SearchRequestSchema,
    SearchResponseSchema,
    SearchResultSchema,
)
from app.search.searxng_client import SearXNGClient

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["search"],
    responses={
        400: {"description": "Invalid request"},
        500: {"description": "Internal server error"},
    },
)


# Dependency injections
async def get_searxng_client() -> SearXNGClient:
    """Dependency injection for SearXNG client"""
    return SearXNGClient()


async def get_dspy_pipeline() -> DSPyPipeline:
    """Dependency injection for DSPy pipeline"""
    return DSPyPipeline()


@router.post(
    "/search",
    response_model=SearchResponseSchema,
    summary="Execute AI-powered search",
    description="Search the web and get structured results with AI insights",
)
async def search(
    request: SearchRequestSchema,
    searxng_client: SearXNGClient = Depends(get_searxng_client),
    dspy_pipeline: DSPyPipeline = Depends(get_dspy_pipeline),
) -> SearchResponseSchema:
    """
    Execute a search query and return structured results

    This endpoint:
    1. Validates the search query
    2. Searches the web using SearXNG
    3. Processes results with AI
    4. Returns structured JSON + Markdown

    Args:
        request: Search request with query and parameters
        searxng_client: SearXNG client (injected)
        dspy_pipeline: AI pipeline (injected)

    Returns:
        SearchResponseSchema with results and AI insights

    Raises:
        HTTPException: 400 if query is invalid, 500 if search fails
    """
    start_time = time.time()

    try:
        logger.info(f"Processing search request: {request.query}")

        # Validate query
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if len(query) > 500:
            raise HTTPException(
                status_code=400, detail="Query too long (max 500 characters)"
            )

        # Perform search
        logger.info(f"Querying SearXNG with: {query}")
        raw_results = await searxng_client.search(
            query=query, limit=request.limit, language=request.language
        )

        if not raw_results:
            logger.warning(f"No results found for: {query}")

        # Process results with AI
        logger.info("Processing results with AI")
        ai_output = await dspy_pipeline.process_results(query, raw_results)

        # Convert raw results to schema
        results = [SearchResultSchema(**result) for result in raw_results]

        # Calculate processing time
        processing_time = time.time() - start_time

        # Build response
        response = SearchResponseSchema(
            query=query,
            results_count=len(results),
            results=results,
            markdown_summary=ai_output["markdown_summary"],
            json_data=ai_output["json_data"],
            insights={
                "key_points": ai_output["key_points"],
                "confidence": ai_output["confidence"],
                "summary": f"Found {len(results)} relevant results for '{query}'",
            },
            processing_time=processing_time,
        )

        logger.info(f"Search completed in {processing_time:.2f}s")
        return response

    except HTTPException:
        raise
    except ConnectionError as e:
        logger.error(f"Connection error with SearXNG: {e}")
        raise HTTPException(status_code=503, detail="Search engine unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in search: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal server error during search"
        )


@router.get(
    "/search/health",
    summary="Check search service health",
)
async def search_health(
    searxng_client: SearXNGClient = Depends(get_searxng_client),
) -> dict:
    """
    Health check for search service

    Returns:
        Status of search dependencies
    """
    try:
        logger.info("Performing health check")

        # Check SearXNG connectivity
        health_status = {
            "status": "healthy",
            "searxng": "unknown",
            "ai": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Try simple search to verify SearXNG
        try:
            results = await searxng_client.search("test", limit=1)
            health_status["searxng"] = "healthy" if results else "no_results"
        except Exception as e:
            logger.warning(f"SearXNG health check failed: {e}")
            health_status["searxng"] = "unhealthy"
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check failed")
