"""
Logging utilities for the agent dashboard.
"""
import logging
import logging.config
from pathlib import Path
from backend.core.config import config

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Custom log format (FastAPI-style)
LOG_FORMAT = "%(levelname)s:     %(name)s.py:%(lineno)d - %(message)s"
# LOG_FORMAT = "%(levelname)s:     %(module)s.%(filename)s.py:%(lineno)d - %(message)s"

# Configure logging based on environment
if config.server.is_production:
    try:
        logging.config.dictConfig(config.server.log_config)
    except Exception as e:
        # Fallback to basic configuration if dictConfig fails
        logging.basicConfig(
            level=getattr(logging, config.server.log_level.upper(), logging.INFO),
            format=LOG_FORMAT,
        )
        logging.warning(
            f"Failed to configure logging from dict config, using fallback: {e}"
        )
else:
    # Simple configuration for development
    logging.basicConfig(
        level=getattr(logging, config.server.log_level.upper(), logging.DEBUG),
        format=LOG_FORMAT,
    )

# Default module logger
logger = logging.getLogger(__name__)

def get_logger(name: str):
    """Get a logger with the given name."""
    return logging.getLogger(name)
