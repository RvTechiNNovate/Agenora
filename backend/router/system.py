from fastapi import APIRouter
from backend.config import config

# Create router
router = APIRouter(prefix="/api", tags=["system"])

@router.get("/health", 
        summary="Health check",
        description="Check if the API is running and healthy.")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": config.server.environment
    }
