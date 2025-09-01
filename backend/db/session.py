"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import config

# Create SQLAlchemy engine and session
engine = create_engine(config.database.url, connect_args=config.database.connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base model
Base = declarative_base()

# Database initialization and session management
def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)

# Create a dependency for database sessions
def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
