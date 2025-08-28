"""
Security utilities for the agent dashboard.
"""
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from backend.config import config

# API key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key for protected endpoints."""
    if not config.security.api_key_enabled:
        return True
        
    if api_key != config.security.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API key"
        )
    
    return True
