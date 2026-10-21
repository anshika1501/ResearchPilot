"""FastAPI application entry point for ResearchPilot AI backend."""

from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from app.schemas.health import HealthResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ResearchPilot AI - AI-powered research and document intelligence platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Root Health Check",
)
def root_health() -> HealthResponse:
    """Root health check endpoint for monitoring and container health checks."""
    return HealthResponse(
        status="ok",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )


# Register API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)
