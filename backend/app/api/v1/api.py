"""Main router aggregation for API v1."""

from fastapi import APIRouter
from app.api.v1.endpoints import chat, documents, health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

