import uvicorn
import os
import logging
from backend.config import config
from backend.database import init_db

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Initialize database
    init_db()
    
    print(f"Starting Agent Dashboard server in {config.server.environment} mode...")
    print(f"Open http://{config.server.host}:{config.server.port} in your browser to access the dashboard")
    
    # Run the application with hot reload in development
    is_dev = config.server.environment.lower() == "development"
    
    # In development mode, use simpler logging config
    if is_dev:
        uvicorn.run(
            "backend.main:app", 
            host=config.server.host, 
            port=config.server.port, 
            reload=True,
            log_level=config.server.log_level.lower()
        )
    else:
        # In production, use the full logging config
        uvicorn.run(
            "backend.main:app", 
            host=config.server.host, 
            port=config.server.port, 
            reload=False,
            log_level=config.server.log_level.lower(),
            log_config=config.server.log_config
        )
