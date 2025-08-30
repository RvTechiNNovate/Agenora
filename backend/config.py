"""
Configuration for the agent dashboard application.
Loads settings from environment variables with sensible defaults.
"""

from pydantic import BaseModel, field_validator
from dotenv import load_dotenv
from backend.configuration import ServerConfig,DatabaseConfig,PerformanceConfig,SecurityConfig

# Load environment variables from .env file if present
load_dotenv()

class Config(BaseModel):
    """Main application configuration."""
    server: ServerConfig = ServerConfig()
    security: SecurityConfig = SecurityConfig()
    database: DatabaseConfig = DatabaseConfig()
    performance: PerformanceConfig = PerformanceConfig()

# Create singleton instance
config = Config()
