"""
Database models for the agent dashboard application.
Uses SQLAlchemy for ORM and database interaction.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, create_engine, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from backend.config import config

# Create SQLAlchemy engine and session
engine = create_engine(config.database.url, connect_args=config.database.connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base model
Base = declarative_base()

class AgentModel(Base):
    """Agent model for database storage."""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    framework = Column(String, default="crewai")
    # Common fields for all frameworks
    model = Column(String)
    model_config = Column(JSON, default={})
    
    # CrewAI specific fields
    role = Column(String, nullable=True)
    backstory = Column(String, nullable=True)
    task = Column(String, nullable=True)
    
    # LangChain specific fields
    agent_type = Column(String, nullable=True)
    tools = Column(JSON, nullable=True)
    
    # Framework-specific configuration (for future frameworks)
    framework_config = Column(JSON, default={})
    status = Column(String, default="stopped")
    error = Column(String, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship with versions
    versions = relationship("AgentVersionModel", back_populates="agent", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        # Base fields that all frameworks have
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "framework": self.framework,
            "model": self.model,
            "model_config": self.model_config,
            "status": self.status,
            "error": self.error,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Add framework-specific fields based on the framework
        if self.framework == "crewai":
            result.update({
                "role": self.role,
                "backstory": self.backstory,
                "task": self.task
            })
        elif self.framework == "langchain":
            result.update({
                "agent_type": self.agent_type,
                "tools": self.tools or []
            })
        
        # Add any additional framework-specific config
        if self.framework_config:
            result.update(self.framework_config)
            
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Create an instance from a dictionary."""
        # Create a base agent with common fields
        agent = cls(
            name=data.get("name"),
            description=data.get("description"),
            framework=data.get("framework", "crewai"),
            model=data.get("model"),
            model_config=data.get("model_config", {}),
            status="stopped",
            version=1
        )
        
        # Add framework-specific fields based on the framework
        framework = data.get("framework", "crewai")
        
        if framework == "crewai":
            agent.role = data.get("role", "Assistant")
            agent.backstory = data.get("backstory")
            agent.task = data.get("task")
        elif framework == "langchain":
            agent.agent_type = data.get("agent_type", "conversational")
            agent.tools = data.get("tools", [])
        
        # Extract any additional fields into framework_config
        framework_config = {}
        for key, value in data.items():
            if key not in ["name", "description", "framework", "model", "model_config", 
                          "role", "backstory", "task", "agent_type", "tools", 
                          "id", "status", "error", "version", "created_at", "updated_at"]:
                framework_config[key] = value
        
        if framework_config:
            agent.framework_config = framework_config
            
        return agent


class AgentVersionModel(Base):
    """Model to store agent versions for versioning history."""
    __tablename__ = "agent_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    framework = Column(String)
    role = Column(String)
    backstory = Column(String, nullable=True)
    task = Column(String, nullable=True)
    model = Column(String)
    model_config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with agent
    agent = relationship("AgentModel", back_populates="versions")
    
    def to_dict(self):
        """Convert the version to a dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "version_number": self.version_number,
            "name": self.name,
            "description": self.description,
            "framework": self.framework,
            "role": self.role,
            "backstory": self.backstory,
            "task": self.task,
            "model": self.model,
            "model_config": self.model_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_agent(cls, agent, version_number):
        """Create a version from an agent instance."""
        return cls(
            agent_id=agent.id,
            version_number=version_number,
            name=agent.name,
            description=agent.description,
            framework=agent.framework,
            role=agent.role,
            backstory=agent.backstory,
            task=agent.task,
            model=agent.model,
            model_config=agent.model_config
        )


# Create all tables
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
