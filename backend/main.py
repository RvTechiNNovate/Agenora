from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, create_model, validator
from typing import Dict, Any, Optional, List, Union, Type, get_type_hints
import os
import logging
import time
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

# Import local modules
from backend.config import config
from backend.database import init_db
from backend.utils.logging import get_logger
from backend.utils.security import verify_api_key
from backend.router.agent import router as agent_router
from backend.router.agent_execution import router as agent_execution_router
from backend.router.framework import router as framework_router
from backend.router.system import router as system_router
from backend.router.settings import router as settings_router



# Set up logging
logger = get_logger(__name__)

# Initialize database before app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize resources before application startup.
    Cleanup resources when application shuts down.
    """
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Yield to FastAPI
    yield
    
    # Cleanup resources
    logger.info("Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="Agent Dashboard API",
    description="API for creating and managing AI agents with CrewAI",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if not config.server.is_production else None,
    redoc_url="/api/redoc" if not config.server.is_production else None,
)

# Include routers
app.include_router(agent_router)
app.include_router(agent_execution_router)
app.include_router(framework_router)
app.include_router(system_router)
app.include_router(settings_router)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request details and timing."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Log request details
    duration = time.time() - start_time
    logger.debug(
        f"{request.method} {request.url.path} "
        f"completed in {duration:.4f}s with status {response.status_code}"
    )
    
    return response

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Root route - serve frontend
@app.get("/", 
        summary="Frontend",
        description="Serve the frontend application.")
async def serve_frontend():
    """Serve the frontend application."""
    return FileResponse("frontend/index.html")
