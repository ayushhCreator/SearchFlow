"""
FastAPI Application Entry Point

This is the main entry point for the SearchFlow application.
It initializes FastAPI and configures all routes and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging

# Initialize logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="SearchFlow",
    description="AI-powered search backend that returns structured knowledge",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "SearchFlow is running"}


@app.get("/health")
async def health():
    """Detailed health check"""
    return {"status": "healthy", "version": "0.1.0", "service": "SearchFlow API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8007)
