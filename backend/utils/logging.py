"""
Logging utilities for the agent dashboard.
"""
import logging
import logging.config
import os
from pathlib import Path
from backend.config import config

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure logging based on environment
if config.server.is_production:
    try:
        logging.config.dictConfig(config.server.log_config)
    except Exception as e:
        # Fallback to basic configuration if the dict config fails
        logging.basicConfig(
            level=getattr(logging, config.server.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.warning(f"Failed to configure logging from dict config: {e}")
else:
    # Simple configuration for development
    logging.basicConfig(
        level=getattr(logging, config.server.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

# Create logger
logger = logging.getLogger(__name__)

def get_logger(name):
    """Get a logger with the given name."""
    return logging.getLogger(name)
