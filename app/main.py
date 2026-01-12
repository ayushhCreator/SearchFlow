"""
FastAPI Application Entry Point

This is the main entry point for the SearchFlow application.
It initializes FastAPI, configures middleware, and mounts all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import search
from app.cache.redis_client import close_cache_client, get_cache_client
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="SearchFlow API",
    description="AI-powered search backend that returns structured knowledge",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions"""
    logger.error(f"Uncaught exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Health endpoints
@app.get("/", tags=["health"])
async def root():
    """Root endpoint - service status"""
    return {"message": "SearchFlow is running", "version": "0.1.0", "docs": "/docs"}


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    cache = await get_cache_client()
    cache_stats = await cache.get_stats()
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "SearchFlow API",
        "cache": cache_stats,
    }


# Include search router
app.include_router(search.router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    logger.info("SearchFlow API starting up")
    logger.info(f"Environment: Debug={settings.DEBUG}")
    logger.info(f"SearXNG URL: {settings.SEARXNG_URL}")

    # Initialize cache
    cache = await get_cache_client()
    if cache._connected:
        logger.info("Cache initialized successfully")
    else:
        logger.warning("Cache not available - running without caching")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info("SearchFlow API shutting down")
    # Cleanup cache connection
    await close_cache_client()
    logger.info("Cache connection closed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8007, log_level=settings.LOG_LEVEL.lower())
