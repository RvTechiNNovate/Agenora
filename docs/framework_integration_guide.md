# Agent Framework Integration Guide

<div align="center">
  
![Agenora Framework Integration](images/framework_integration.png)

</div>

This document provides detailed instructions for integrating a new agent framework into Agenora.

## Architecture Overview

The dashboard follows a modular architecture for agent frameworks:

1. **Base Agent Manager**: Defines the common interface and functionality for all agent managers
2. **Framework-Specific Managers**: Implement the interface for specific frameworks (CrewAI, LangChain, etc.)
3. **Configuration Classes**: Standardize configuration handling for each framework
4. **Database Models**: Store framework-specific configuration in the database
5. **Factory Pattern**: Dynamically loads available agent providers

## Integration Steps

### 1. Plan Your Integration

Before starting, identify:

- What configuration parameters your framework needs
- How agents are created and managed in your framework
- What API endpoints are required for your framework
- How queries are executed in your framework

### 2. Create the Framework Directory

```bash
mkdir -p backend/agent_manager/providers/your_framework_name
touch backend/agent_manager/providers/your_framework_name/__init__.py
```

### 3. Create the Configuration Class

Create `config.py` in your framework directory with a configuration class:

```python
from typing import List, Dict, Any, Optional

class YourFrameworkConfig:
    """Configuration for YourFramework agents."""
    
    def __init__(
        self, 
        param1: str,
        param2: Optional[List[str]] = None,
        # Add other parameters
    ):
        self.param1 = param1
        self.param2 = param2 or []
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "YourFrameworkConfig":
        return cls(
            param1=config_dict.get("param1", ""),
            param2=config_dict.get("param2", []),
        )
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "param1": self.param1,
            "param2": self.param2,
        }
```

### 4. Create the Database Model

Add your framework's model to `backend/models.py`:

```python
class YourFrameworkAgentModel(Base):
    """YourFramework specific agent configuration."""
    __tablename__ = "your_framework_agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    param1 = Column(String)
    param2 = Column(JSON, default=lambda: [])
    
    # Relationship back to main agent
    agent = relationship("AgentModel", back_populates="your_framework_config")

    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "param1": self.param1,
            "param2": self.param2,
        }

    @classmethod
    def from_dict(cls, data, agent_id):
        return cls(
            agent_id=agent_id,
            param1=data.get("param1", ""),
            param2=data.get("param2", []),
        )
```

Also add the relationship to the `AgentModel` class:

```python
your_framework_config = relationship("YourFrameworkAgentModel", 
                                    back_populates="agent", 
                                    uselist=False, 
                                    cascade="all, delete-orphan")
```

And update the `to_dict` method:

```python
elif self.framework == "your_framework" and self.your_framework_config:
    framework_config = {
        "param1": self.your_framework_config.param1,
        "param2": self.your_framework_config.param2,
    }
```

### 5. Create the Framework Manager

Create `your_framework_agent.py` in your framework directory:

```python
from typing import Dict, Any, Optional, List, Union
from sqlalchemy.orm import Session
from backend.agent_manager.base import BaseAgentManager
from backend.db.session import SessionLocal
from backend.models import AgentModel, YourFrameworkAgentModel
from backend.core.logging import get_logger
from backend.schemas import FrameworkSchema
from .config import YourFrameworkConfig

logger = get_logger(__name__)

class YourFrameworkManager(BaseAgentManager):
    @property
    def framework_name(self) -> str:
        return "your_framework"
    
    # Implement all required methods from BaseAgentManager
    # ...

    def _create_framework_config(self, db: Session, db_agent: AgentModel, config: Dict[str, Any]) -> None:
        framework_config_obj = YourFrameworkConfig.from_dict(config)
        framework_model = YourFrameworkAgentModel.from_dict(framework_config_obj.to_dict(), db_agent.id)
        db.add(framework_model)
    
    def _get_framework_config(self, agent: AgentModel) -> Dict[str, Any]:
        if agent.your_framework_config:
            return agent.your_framework_config.to_dict()
        return {}
    
    def _update_framework_config(self, db: Session, db_agent: AgentModel, config: Dict[str, Any]) -> None:
        # Update framework-specific configuration
        # ...

# Instantiate the manager
manager = YourFrameworkManager()
```


### 6. Test Your Integration

1. Start the application
2. Create an agent with your framework
3. Start the agent
4. Send queries to the agent
5. Stop and delete the agent

### 7. Document Your Framework

Update the documentation to include information about your framework:

- Configuration parameters
- Required dependencies
- Supported features
- Usage examples

## Best Practices

1. **Error Handling**: Provide meaningful error messages and handle exceptions gracefully
2. **Logging**: Use the logger to record important events
3. **Validation**: Validate all inputs to prevent errors
4. **Documentation**: Comment your code and update documentation
5. **Testing**: Write tests for your framework integration

## Resources

- [BaseAgentManager Documentation](../backend/agent_manager/base.py)
- [Models Documentation](../backend/models.py)
- [Existing Framework Implementations](../backend/agent_manager/agent_providers/)
