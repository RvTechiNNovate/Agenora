"""
Configuration for the agent dashboard application.
Loads settings from environment variables with sensible defaults.
"""
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class ServerConfig(BaseModel):
    """Server configuration settings."""
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_production(self) -> bool:
        """Check if the application is running in production."""
        return self.environment.lower() == "production"
    
    @property
    def log_config(self) -> dict:
        """Get the logging configuration based on environment."""
        # Define base configuration
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "fmt": "%(levelprefix)s %(asctime)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "access": {
                    "fmt": "%(levelprefix)s %(asctime)s | %(client_addr)s - %(request_line)s %(status_code)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "": {"handlers": ["default"], "level": self.log_level},
                "uvicorn.access": {"handlers": ["access"], "level": "INFO"},
            },
        }
        
        # Add file handler only in production
        if self.is_production:
            config["handlers"]["file"] = {
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/agent_dashboard.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            }
            config["loggers"][""]["handlers"] = ["default", "file"]
            
        return config

class SecurityConfig(BaseModel):
    """Security configuration settings."""
    api_key_enabled: bool = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
    api_key: Optional[str] = os.getenv("API_KEY", None)
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",")
    
    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: Optional[str], values) -> Optional[str]:
        """Validate API key if enabled."""
        if values.data.get("api_key_enabled", False) and (not v or len(v) < 16):
            raise ValueError("API key must be at least 16 characters when API key auth is enabled")
        return v

class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    url: str = os.getenv("DATABASE_URL", "sqlite:///./agents.db")
    connect_args: dict = {"check_same_thread": False}  # For SQLite

class PerformanceConfig(BaseModel):
    """Performance configuration settings."""
    worker_timeout: int = int(os.getenv("WORKER_TIMEOUT", "300"))
    max_workers: int = int(os.getenv("MAX_WORKERS", "4"))
    keepalive: int = int(os.getenv("KEEPALIVE", "65"))

class Config(BaseModel):
    """Main application configuration."""
    server: ServerConfig = ServerConfig()
    security: SecurityConfig = SecurityConfig()
    database: DatabaseConfig = DatabaseConfig()
    performance: PerformanceConfig = PerformanceConfig()

# Create singleton instance
config = Config()
