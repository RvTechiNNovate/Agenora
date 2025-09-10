from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from backend.schemas.schemas import FrameworkResponse
from backend.services.framework_service import FrameworkService

# Create router
router = APIRouter(prefix="/api", tags=["frameworks"])

@router.get("/frameworks/schema",
        summary="Get available frameworks and their schemas",
        response_model=FrameworkResponse,
        description="Returns the list of supported agent frameworks and their input schemas.")
async def get_framework_schemas():
    """Get all available frameworks and their schemas."""
    try:
        return FrameworkService.get_framework_schemas()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/frameworks",
        summary="Get available frameworks",
        description="Returns the list of supported agent frameworks.")
async def get_frameworks():
    """Get all available frameworks."""
    try:
        return FrameworkService.get_frameworks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching frameworks: {str(e)}")

@router.get("/llm/providers",
        summary="List available LLM providers",
        description="Get a list of all supported LLM providers.")
async def list_llm_providers():
    """List all supported LLM providers."""
    try:
        return FrameworkService.list_llm_providers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching LLM providers: {str(e)}")

@router.get("/llm/models",
        summary="List available LLM models",
        description="Get a list of available models, optionally filtered by provider.")
async def list_llm_models(provider: Optional[str] = None):
    """List available models for a provider or all providers."""
    try:
        return FrameworkService.list_llm_models(provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching LLM models: {str(e)}")
