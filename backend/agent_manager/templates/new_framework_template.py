"""
Template for creating new agent providers.

To create a new agent provider:
1. Create a new directory under backend/agent_manager/agent_providers/{your_framework_name}/
2. Copy this template to {your_framework_name}_agent.py
3. Copy the config_template.py to config.py and customize it
4. Implement all the required methods
5. Create any necessary models in models.py (see example in AgnoAgentModel, CrewAIAgentModel, etc.)
6. Register your models in main.py if needed

The plugin manager will automatically discover and register your agent provider.
"""
from typing import Dict, Any, Optional, List, Union
from sqlalchemy.orm import Session
from backend.agent_manager.base import BaseAgentManager
from backend.db.session import SessionLocal
from backend.db.models import AgentModel  # Import your framework-specific model too
from backend.core.logging import get_logger
from backend.schemas.schemas import FrameworkSchema
# Import your config class
from .config import NewFrameworkConfig

# Set up logger
logger = get_logger(__name__)

# Set flag to check if framework is available
FRAMEWORK_AVAILABLE = True
try:
    # Try importing required packages
    import new_framework_package
except ImportError:
    FRAMEWORK_AVAILABLE = False
    logger.warning("New Framework is not available. Please install it with: pip install new-framework-package")

# Define any constants or tool mappings
AVAILABLE_TOOLS = {
    # Add framework-specific tools
    "tool1": {"description": "Description of tool 1"},
    "tool2": {"description": "Description of tool 2"},
}

class NewFrameworkManager(BaseAgentManager):
    """Manager for NewFramework agents."""
    
    @property
    def framework_name(self) -> str:
        """Return the name of the framework this manager handles."""
        return "new_framework"  # Replace with your framework's name
    
    def __init__(self):
        """Initialize the NewFramework manager."""
        # Check if framework is available before initializing
        if not FRAMEWORK_AVAILABLE:
            logger.warning("New Framework is not available. Please install it with: pip install new-framework-package")
        
        # Initialize any framework-specific properties
        self.instances = {}  # For storing runtime instances
        
        # Call parent initializer last (it will call _load_agents_from_db)
        super().__init__()
    
    def get_schema(self) -> Any:
        """
        Get the schema for this framework.
        
        Returns:
            A FrameworkSchema object describing the fields required by this framework.
        """
        return FrameworkSchema(
            name="New Framework",  # User-friendly name
            description="Description of the new framework",
            fields={
                # Define the fields specific to your framework
                "field1": str,
                "field2": List[str],
                "field3": bool,
            }
        )
    
    def validate_agent_config(self, config: Dict[str, Any]) -> Union[bool, str]:
        """
        Validate the given agent configuration.
        
        Args:
            config: The configuration to validate
            
        Returns:
            True if the configuration is valid, otherwise an error message
        """
        # Check for required fields
        required_fields = ["field1", "model"]
        for field in required_fields:
            if field not in config:
                return f"Missing required field: {field}"
        
        # Add additional validation logic specific to your framework
        # For example, validate model format, field types, etc.
        
        # If valid, return True
        return True
    
    def _create_framework_config(self, db: Session, db_agent: AgentModel, config: Dict[str, Any]) -> None:
        """
        Create framework-specific configuration for the agent.
        
        Args:
            db: Database session
            db_agent: Agent model instance
            config: Agent configuration
        """
        # Create config object for better validation and defaults
        framework_config_obj = NewFrameworkConfig.from_dict(config)
        
        # Create database model from config object
        # Replace NewFrameworkAgentModel with your actual model class
        from backend.db.models import NewFrameworkAgentModel
        framework_model = NewFrameworkAgentModel.from_dict(framework_config_obj.to_dict(), db_agent.id)
        db.add(framework_model)
    
    def _get_framework_config(self, agent: AgentModel) -> Dict[str, Any]:
        """
        Get framework-specific configuration for the agent.
        
        Args:
            agent: Agent model instance
            
        Returns:
            Dictionary containing framework-specific configuration
        """
        # Replace new_framework_config with your framework's property name
        if hasattr(agent, "new_framework_config") and agent.new_framework_config:
            return agent.new_framework_config.to_dict()
        return {}
    
    def _update_framework_config(self, db: Session, db_agent: AgentModel, config: Dict[str, Any]) -> None:
        """
        Update framework-specific configuration for the agent.
        
        Args:
            db: Database session
            db_agent: Agent model instance
            config: Updated agent configuration
        """
        # Ensure the framework-specific config exists
        # Replace new_framework_config with your framework's property name
        if not hasattr(db_agent, "new_framework_config") or not db_agent.new_framework_config:
            error_msg = f"Agent {db_agent.id} does not have New Framework configuration"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Get current config values
        current_config = db_agent.new_framework_config.to_dict()
        
        # Merge with new config values
        merged_config = {**current_config, **config}
        framework_config_obj = NewFrameworkConfig.from_dict(merged_config)
        
        # Update fields individually to preserve the existing record
        # Replace with your framework's specific fields
        db_agent.new_framework_config.field1 = framework_config_obj.field1
        db_agent.new_framework_config.field2 = framework_config_obj.field2
        db_agent.new_framework_config.field3 = framework_config_obj.field3
    
    def _run_query(self, agent_id: int, query: str) -> str:
        """
        Execute a query with an agent.
        
        Args:
            agent_id: The ID of the agent to query
            query: The query string
            
        Returns:
            The response from the agent
        """
        if not FRAMEWORK_AVAILABLE:
            return "New Framework is not available. Please install it with: pip install new-framework-package"
            
        if agent_id not in self.agents or self.agents[agent_id]["instance"] is None:
            return "Agent not initialized. Please start the agent first."
            
        try:
            # Get the agent instance
            agent_instance = self.agents[agent_id]["instance"]
            
            # Execute the query using your framework's API
            # This is just an example, replace with actual code for your framework
            result = agent_instance.run(query)
            
            # Log success
            logger.info(f"Successfully executed query for agent {agent_id}")
            
            # Return the result
            return result
        except Exception as e:
            logger.error(f"Error executing query with New Framework agent: {str(e)}")
            return f"Error: {str(e)}"
    
    def start_agent(self, agent_id: int) -> bool:
        """
        Start an agent.
        
        Args:
            agent_id: The ID of the agent to start
            
        Returns:
            True if the agent was started successfully, False otherwise
        """
        if not FRAMEWORK_AVAILABLE:
            logger.error("New Framework is not available. Please install it with: pip install new-framework-package")
            self.agents[agent_id]["error"] = "New Framework is not available"
            super().update_agent_status(agent_id, "error", "New Framework is not available")
            return False
            
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False
            
        try:
            # Get agent configuration
            config = self.agents[agent_id]["config"]
            
            # Convert to framework-specific config object for better typing and validation
            framework_config = NewFrameworkConfig.from_dict(config)
            
            # Set up language model
            model_name = config.get("model", "default-model")
            model_config = config.get("model_config", {})
            
            # Parse provider from model string if specified (e.g. "openai:gpt-4")
            provider_name = None
            if ":" in model_name:
                parts = model_name.split(":", 1)
                provider_name, model_name = parts
            
            # Initialize your framework's components
            # This is just an example, replace with actual initialization code
            from new_framework_package import Agent  # Replace with actual import
            
            # Create framework-specific agent
            agent = Agent(
                model=model_name,
                field1=framework_config.field1,
                field2=framework_config.field2,
                field3=framework_config.field3
            )
            
            # Store agent instance
            self.agents[agent_id]["instance"] = agent
            self.agents[agent_id]["status"] = "running"
            
            # Update database status
            super().update_agent_status(agent_id, "running")
            
            logger.info(f"Started New Framework agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting New Framework agent {agent_id}: {str(e)}")
            self.agents[agent_id]["error"] = str(e)
            super().update_agent_status(agent_id, "error", str(e))
            return False
    
    def _cleanup_agent_resources(self, agent_id: int):
        """
        Clean up resources for an agent.
        
        Args:
            agent_id: The ID of the agent to clean up
        """
        # Remove any framework-specific resources
        if agent_id in self.instances:
            del self.instances[agent_id]
        
        # Clean up the agent instance
        if agent_id in self.agents:
            self.agents[agent_id]["instance"] = None
        
        # Update status to stopped
        super().update_agent_status(agent_id, "stopped")

# Instantiate the manager
manager = NewFrameworkManager()
