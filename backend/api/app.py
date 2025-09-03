from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import time
from contextlib import asynccontextmanager

# Import local modules
from backend.core.config import config
from backend.db.session import init_db
from backend.core.logging import get_logger
from backend.api.routes import (
    agent_router,
    agent_execution_router,
    framework_router,
    system_router,
    settings_router
)


# Set up logging
logger = get_logger(__name__)

# Initialize database and resources before app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize resources before application startup.
    Cleanup resources when application shuts down.
    """
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Log available agent providers
    from backend.agent_manager import managers
    logger.info(f"Available agent providers: {', '.join(managers.keys())}")
    
    # Yield to FastAPI
    yield
    
    # Cleanup resources
    logger.info("Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="Agent Dashboard API",
    description="API for creating and managing AI agents",
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
