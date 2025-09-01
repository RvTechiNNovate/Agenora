from fastapi import APIRouter, Depends
from typing import List, Optional

from backend.core.config import config
from backend.utils.security import verify_api_key
from backend.agent_manager import managers
from backend.schemas.schemas import FrameworkResponse, FrameworkSchema
from backend.llm_manager.manager import llm_provider_manager
# Create router
router = APIRouter(prefix="/api", tags=["frameworks"])

@router.get("/frameworks/schema",
        summary="Get available frameworks and their schemas",
        response_model=FrameworkResponse,
        description="Returns the list of supported agent frameworks and their input schemas.")
async def get_framework_schemas():
    """Get all available frameworks and their schemas."""
    # Fetch framework schemas from agent managers
    frameworks = {}
    
    # Common fields for all frameworks
    common_fields = {
        "name": str,
        "description": str,
        "framework": str,
        "model": str,
        "model_config": dict
    }
    
    # Get schema from each manager dynamically
    for framework_name, manager in managers.items():
        if hasattr(manager, 'get_schema'):
            # Use the manager's get_schema method if available
            schema = manager.get_schema()
            frameworks[framework_name] = schema
        else:
            raise ValueError(f"Manager for {framework_name} does not implement get_schema()")

    return FrameworkResponse(
        frameworks=frameworks,
        common_fields=common_fields
    )

@router.get("/frameworks",
        summary="Get available frameworks",
        description="Returns the list of supported agent frameworks.")
async def get_frameworks():
    """Get all available frameworks."""
    return {
        "frameworks": list(managers.keys())
    }

@router.get("/llm/providers",
        summary="List available LLM providers",
        description="Get a list of all supported LLM providers.")
async def list_llm_providers():
    """List all supported LLM providers."""
    return {"providers": llm_provider_manager.list_providers()}

@router.get("/llm/models",
        summary="List available LLM models",
        description="Get a list of available models, optionally filtered by provider.")
async def list_llm_models(provider: Optional[str] = None):
    """List available models for a provider or all providers."""
    return {"models": llm_provider_manager.list_models(provider)}
