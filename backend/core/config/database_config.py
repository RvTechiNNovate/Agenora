import os
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    url: str = os.getenv("DATABASE_URL", "sqlite:///./Agenora.db")
    connect_args: dict = {"check_same_thread": False}  # For SQLite
