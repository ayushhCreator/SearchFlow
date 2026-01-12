"""
Export Routes

API endpoints for structured output (JSON/Markdown).
Single Responsibility: Only handles export endpoints.
"""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.api.models import ExportRequest
from app.output import format_as_json, format_as_markdown
from app.services import get_search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["export"])


@router.post("/search/json")
async def search_json(request: ExportRequest):
    """
    Search and return structured JSON output.

    Returns a well-formatted JSON document suitable for:
    - Programmatic consumption
    - Data pipelines
    - API integrations
    """
    try:
        service = await get_search_service()
        result = await service.search(
            query=request.query,
            skip_cache=request.skip_cache,
            include_context=request.include_context,
        )
        return format_as_json(result)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=503, detail="Search service not configured.")
    except Exception as e:
        logger.error(f"JSON export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/markdown")
async def search_markdown(request: ExportRequest):
    """
    Search and return Markdown document.

    Returns a well-formatted Markdown document suitable for:
    - Documentation
    - Notes and reports
    - Knowledge base entries
    """
    try:
        service = await get_search_service()
        result = await service.search(
            query=request.query,
            skip_cache=request.skip_cache,
            include_context=request.include_context,
        )
        markdown = format_as_markdown(result)

        return PlainTextResponse(
            content=markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": "inline; filename=search_result.md"},
        )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=503, detail="Search service not configured.")
    except Exception as e:
        logger.error(f"Markdown export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
