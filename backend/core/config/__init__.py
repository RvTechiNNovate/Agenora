"""
Configuration management for Agenora.
Import the config object from this module to access all configuration settings.
"""
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables globally
load_dotenv()

# Import all configuration components
from .database_config import DatabaseConfig
from .server_config import SecurityConfig
from .server_config import PerformanceConfig
from .server_config import ServerConfig

"""
Configuration for the agent dashboard application.
Loads settings from environment variables with sensible defaults.
"""

class Config(BaseModel):
    """Main application configuration."""
    server: ServerConfig = ServerConfig()
    security: SecurityConfig = SecurityConfig()
    database: DatabaseConfig = DatabaseConfig()
    performance: PerformanceConfig = PerformanceConfig()

# Create singleton instance
config = Config()


# Make config importable directly from the config module
__all__ = ["config"]