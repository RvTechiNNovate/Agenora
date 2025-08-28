import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.llm_providers.providers.config import llm_config
router = APIRouter(prefix="/api", tags=["settings"])

class Settings(BaseModel):
    """Settings model for API keys."""
    openai_api_key: str | None = None
    azure_api_key: str | None = None
    azure_endpoint: str | None = None
    groq_api_key: str | None = None

@router.get("/settings")
async def get_settings():
    """Get the current API key settings."""
    return {
        "openai_api_key": llm_config.openai_api_key,
        "azure_api_key": llm_config.azure_api_key,
        "azure_endpoint": llm_config.azure_endpoint,
        "groq_api_key": llm_config.groq_api_key
    }

@router.post("/settings")
async def save_settings(settings: Settings):
    """Save API key settings and update environment variables."""
    # Update config and environment variables
    if settings.openai_api_key is not None:
        llm_config.openai_api_key = settings.openai_api_key
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        
    if settings.azure_api_key is not None:
        llm_config.azure_api_key = settings.azure_api_key
        os.environ["AZURE_OPENAI_API_KEY"] = settings.azure_api_key
        
    if settings.azure_endpoint is not None:
        llm_config.azure_endpoint = settings.azure_endpoint
        os.environ["AZURE_OPENAI_ENDPOINT"] = settings.azure_endpoint
        
    if settings.groq_api_key is not None:
        llm_config.groq_api_key = settings.groq_api_key
        os.environ["GROQ_API_KEY"] = settings.groq_api_key
    
    # Update environment variables
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    
    return {"message": "Settings saved successfully"}
