"""
All database models for the agent dashboard application.
Uses SQLAlchemy for ORM and database interaction.

This file contains all models to avoid circular import issues.
"""
from sqlalchemy import (
    Column, 
    Integer,
    String,
    Float,
    Boolean,
    JSON,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.orm import relationship
import datetime
from backend.db.session import Base

class AgentModel(Base):
    """Base agent model with common fields."""
    __tablename__ = "agents"
    # __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    framework = Column(String, nullable=False) 
    model = Column(String, nullable=False)
    model_config = Column(JSON, default={})
    status = Column(String, default="stopped")
    error = Column(String, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships to framework-specific configurations
    crewai_config = relationship("CrewAIAgentModel", back_populates="agent", uselist=False, cascade="all, delete-orphan")
    langchain_config = relationship("LangChainAgentModel", back_populates="agent", uselist=False, cascade="all, delete-orphan")
    agno_config = relationship("AgnoAgentModel", back_populates="agent", uselist=False, cascade="all, delete-orphan")
    langgraph_config = relationship("LanggraphAgentModel", back_populates="agent", uselist=False, cascade="all, delete-orphan")
    # Relationship with versions
    versions = relationship("AgentVersionModel", back_populates="agent", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert the model to a dictionary."""
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
        
        # Add framework-specific fields
        if self.framework == "crewai" and self.crewai_config:
            result.update({
                "role": self.crewai_config.role,
                "backstory": self.crewai_config.backstory,
                "task": self.crewai_config.task,
                "goals": self.crewai_config.goals,
                "tools": self.crewai_config.tools,
                "memory_enabled": self.crewai_config.memory_enabled,
                "expected_output": self.crewai_config.expected_output
            })
        elif self.framework == "langchain" and self.langchain_config:
            result.update({
                "agent_type": self.langchain_config.agent_type,
                "tools": self.langchain_config.tools,
                "memory_type": self.langchain_config.memory_type,
                "verbose": self.langchain_config.verbose,
                "chain_type": self.langchain_config.chain_type
            })
        elif self.framework == "agno" and self.agno_config:
            result.update({
                "tools": self.agno_config.tools,
                "instructions": self.agno_config.instructions,
                "markdown": self.agno_config.markdown,
                "stream": self.agno_config.stream
            })
        elif self.framework == "langgraph" and self.langgraph_config:
            result.update({
                "tools": self.langgraph_config.tools,
                "prompt": self.langgraph_config.prompt
            })

        return result
        
    @classmethod
    def from_dict(cls, data):
        """Create an instance from a dictionary and associated framework-specific config."""
        # Create base agent with common fields
        agent = cls(
            name=data.get("name"),
            description=data.get("description"),
            framework=data.get("framework"),
            model=data.get("model"),
            model_config=data.get("model_config", {}),
            status="stopped",
            version=1
        )
        
        return agent

class CrewAIAgentModel(Base):
    """CrewAI specific agent configuration."""
    __tablename__ = "crewai_agents"
    # __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    role = Column(String, default="Assistant")
    backstory = Column(Text)
    task = Column(Text)
    goals = Column(JSON, default=lambda: [])
    tools = Column(JSON, default=lambda: [])
    memory_enabled = Column(Boolean, default=True)
    expected_output = Column(Text, nullable=True)
    
    # Relationship back to main agent
    agent = relationship("AgentModel", back_populates="crewai_config")
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "role": self.role,
            "backstory": self.backstory,
            "task": self.task,
            "goals": self.goals,
            "tools": self.tools,
            "memory_enabled": self.memory_enabled,
            "expected_output": self.expected_output
        }
    
    @classmethod
    def from_dict(cls, data, agent_id):
        """Create an instance from a dictionary."""
        return cls(
            agent_id=agent_id,
            role=data.get("role"),
            backstory=data.get("backstory"),
            task=data.get("task"),
            goals=data.get("goals", []),
            tools=data.get("tools", []),
            memory_enabled=data.get("memory_enabled", False),
            expected_output=data.get("expected_output")
        )

class LangChainAgentModel(Base):
    """LangChain specific agent configuration."""
    __tablename__ = "langchain_agents"
    # __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    agent_type = Column(String, default="conversational")
    tools = Column(JSON, default=lambda: [])
    memory_type = Column(String, nullable=True)
    verbose = Column(Boolean, default=False)
    chain_type = Column(String, nullable=True)
    
    # Relationship back to main agent
    agent = relationship("AgentModel", back_populates="langchain_config")
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "tools": self.tools,
            "memory_type": self.memory_type,
            "verbose": self.verbose,
            "chain_type": self.chain_type
        }
    
    @classmethod
    def from_dict(cls, data, agent_id):
        """Create an instance from a dictionary."""
        return cls(
            agent_id=agent_id,
            agent_type=data.get("agent_type", "conversational"),
            tools=data.get("tools", []),
            memory_type=data.get("memory_type"),
            verbose=data.get("verbose", False),
            chain_type=data.get("chain_type")
        )

class AgnoAgentModel(Base):
    """Agno specific agent configuration."""
    __tablename__ = "agno_agents"
    # __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    tools = Column(JSON, default=lambda: [])
    instructions = Column(JSON, default=lambda: [])
    markdown = Column(Boolean, default=True)
    stream = Column(Boolean, default=False)
    
    # Relationship back to main agent
    agent = relationship("AgentModel", back_populates="agno_config")
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "tools": self.tools,
            "instructions": self.instructions,
            "markdown": self.markdown,
            "stream": self.stream
        }
    
    @classmethod
    def from_dict(cls, data, agent_id):
        """Create an instance from a dictionary."""
        return cls(
            agent_id=agent_id,
            tools=data.get("tools", []),
            instructions=data.get("instructions", []),
            markdown=data.get("markdown", True),
            stream=data.get("stream", False)
        )

class LanggraphAgentModel(Base):
    """Langgraph specific agent configuration."""
    __tablename__ = "langgraph_agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    tools = Column(JSON, default=lambda: [])
    prompt = Column(JSON, default=lambda: [])
    
    # Relationship back to main agent
    agent = relationship("AgentModel", back_populates="langgraph_config")

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "tools": self.tools,
            "prompt": self.prompt
        }

    @classmethod
    def from_dict(cls, data, agent_id):
        """Create an instance from a dictionary."""
        return cls(
            agent_id=agent_id,
            tools=data.get("tools", []),
            prompt=data.get("prompt", [])
        )

class AgentVersionModel(Base):
    """Model to store agent versions for versioning history."""
    __tablename__ = "agent_versions"
    # __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    framework = Column(String, nullable=False)
    model = Column(String, nullable=False)
    model_config = Column(JSON, default={})
    framework_config = Column(JSON, default={})  # Store framework-specific config as JSON
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with agent
    agent = relationship("AgentModel", back_populates="versions")
    
    def to_dict(self):
        """Convert the version to a dictionary."""
        version_dict = {
            "id": self.id,
            "agent_id": self.agent_id,
            "version_number": self.version_number,
            "name": self.name,
            "description": self.description,
            "framework": self.framework,
            "model": self.model,
            "model_config": self.model_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        # Add framework-specific config if available
        if self.framework_config:
            version_dict.update(self.framework_config)
            
        return version_dict
    
    @classmethod
    def from_dict(cls, agent, version_number):
        """Create a version from an agent instance."""
        # Start with base fields
        version = cls(
            agent_id=agent.id,
            version_number=version_number,
            name=agent.name,
            description=agent.description,
            framework=agent.framework,
            model=agent.model,
            model_config=agent.model_config
        )
        
        # Add framework-specific config based on framework type
        if agent.framework == "crewai" and agent.crewai_config:
            version.framework_config = {
                "role": agent.crewai_config.role,
                "backstory": agent.crewai_config.backstory,
                "task": agent.crewai_config.task,
                "goals": agent.crewai_config.goals,
                "tools": agent.crewai_config.tools,
                "memory_enabled": agent.crewai_config.memory_enabled,
                "expected_output": agent.crewai_config.expected_output
            }
        elif agent.framework == "langchain" and agent.langchain_config:
            version.framework_config = {
                "agent_type": agent.langchain_config.agent_type,
                "tools": agent.langchain_config.tools,
                "memory_type": agent.langchain_config.memory_type,
                "verbose": agent.langchain_config.verbose,
                "chain_type": agent.langchain_config.chain_type
            }
        elif agent.framework == "agno" and agent.agno_config:
            version.framework_config = {
                "tools": agent.agno_config.tools,
                "instructions": agent.agno_config.instructions,
                "markdown": agent.agno_config.markdown,
                "stream": agent.agno_config.stream
            }
        elif agent.framework == "langgraph" and agent.langgraph_config:
            version.framework_config = {
                "tools": agent.langgraph_config.tools,
                "prompt": agent.langgraph_config.prompt
            }
            
        return version

class SettingModel(Base):
    """Model for storing application settings."""
    __tablename__ = "settings"
    # __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)  # e.g., "llm_provider", "agent", etc.
    provider = Column(String, nullable=False)  # e.g., "azure", "openai", etc.
    key = Column(String, nullable=False)
    value = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
