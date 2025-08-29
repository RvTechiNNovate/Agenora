import os
from fastapi import APIRouter, HTTPException, Depends
from backend.llm_providers.providers.config import llm_config
from pydantic import BaseModel
from backend.schemas import Settings as SchemaSettings
from backend.database import get_db, SessionLocal
from backend.models import SettingModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["settings"])

class ApiSettings(BaseModel):
    """Settings model for API keys."""
    openai_api_key: str | None = None
    azure_api_key: str | None = None
    azure_endpoint: str | None = None
    groq_api_key: str | None = None

@router.get("/settings")
async def get_settings(db: Session = Depends(get_db)):
    """Get the current API key settings."""
    # Create a settings dictionary
    settings = {
        "openai_api_key": llm_config.openai_api_key,
        "azure_api_key": llm_config.azure_api_key,
        "azure_endpoint": llm_config.azure_endpoint,
        "groq_api_key": llm_config.groq_api_key
    }
    
    # Try to load settings from the database
    db_settings = db.query(SettingModel).filter(SettingModel.category == "llm_provider").all()
    
    # Update settings from database values if they exist
    for setting in db_settings:
        if setting.provider == "openai" and setting.key == "api_key":
            settings["openai_api_key"] = setting.value
        elif setting.provider == "azure" and setting.key == "api_key":
            settings["azure_api_key"] = setting.value
        elif setting.provider == "azure" and setting.key == "endpoint":
            settings["azure_endpoint"] = setting.value
        elif setting.provider == "groq" and setting.key == "api_key":
            settings["groq_api_key"] = setting.value
    
    return settings

@router.post("/settings")
async def save_settings(settings: ApiSettings):
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
