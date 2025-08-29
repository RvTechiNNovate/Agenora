"""
Agno agent manager module.
"""
from typing import Dict, Any, Optional, List, Union
from backend.agent_manager.base import BaseAgentManager
from backend.database import SessionLocal
from backend.models import AgentModel, AgnoAgentModel
from backend.utils.logging import get_logger
from .config import AgnoConfig
from backend.schemas import FrameworkSchema
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat

AGNO_AVAILABLE=True

logger = get_logger(__name__)

# Mapping of available tools
AVAILABLE_TOOLS = {
   
}



class AgnoManager(BaseAgentManager):
    """Manager for Agno agents."""
    
    @property
    def framework_name(self):
        return "agno"
    
    def get_schema(self) -> Any:
        """Get the schema for Agno framework."""

        
        return FrameworkSchema(
            name="Agno",
            description="Framework for building advanced agents with tool use",
            fields={
                "instructions": List[str],
                "tools": List[str],
                "markdown": bool,
                "stream": bool
            }
        )
    
    def __init__(self):
        """Initialize the Agno manager."""
        if not AGNO_AVAILABLE:
            logger.warning("Agno is not available. Please install it with: pip install agno")
        super().__init__()
        
    def validate_agent_config(self, config: Dict[str, Any]) -> Any:
        """Validate Agno agent configuration."""
        # Check for required fields based on AgnoConfig
        required_fields = ["model", "instructions"]
        for field in required_fields:
            if field not in config:
                return f"Missing required field: {field}"
        
        # Validate model format
        if "model" in config:
            model_info = config.get("model")
            if not isinstance(model_info, str) or ":" not in model_info:
                return "Model must be in format 'provider:model_id' (e.g., 'openai:gpt-4')"
        
        # Validate instructions is a list
        if "instructions" in config and not isinstance(config["instructions"], list):
            return "Instructions must be a list of strings"
            
        # Validate tools is a list if present
        if "tools" in config and not isinstance(config["tools"], list):
            return "Tools must be a list"
            
        # If we got here, configuration is valid
        return True
    
    def _run_query(self, agent_id: int, query: str) -> str:
        """Execute a query with an Agno agent."""
        if not AGNO_AVAILABLE:
            return "Agno is not available. Please install it with: pip install agno"
            
        if agent_id not in self.agents or self.agents[agent_id]["instance"] is None:
            return "Agent not initialized. Please start the agent first."
            
        try:
            # Get the Agno agent instance
            agent_instance = self.agents[agent_id]["instance"]
            
            # Execute the query
            agent_instance.print_response(query, stream=False)
            result=agent_instance.run_response
            # print(result.content)
            return result.content
        except Exception as e:
            logger.error(f"Error executing query with Agno agent: {str(e)}")
            return f"Error: {str(e)}"
    
    def start_agent(self, agent_id: int) -> bool:
        """Start an Agno agent."""
        if not AGNO_AVAILABLE:
            logger.error("Agno is not available. Please install it with: pip install agno")
            return False
            
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False
            
        try:
            # Get agent configuration
            config = self.agents[agent_id]["config"]
            
            # Convert to AgnoConfig object for better typing and validation
            agno_config = AgnoConfig.from_dict(config)
            
            # Get model information
            model_info = config.get("model", "openai:gpt-3.5-turbo").lower()
            model_type, model_id = model_info.split(":")

            logger.info(f"Agno model ID: {model_id} and model type: {model_type}")

            if model_type == "openai":
                model = OpenAIChat(id=model_id)
            else:
                logger.error(f"Unknown model type: {model_type}")
                return False
            
            # Create tool instances
            tool_instances = []
            
            
            # Create Agno agent using our configuration object
            agent = Agent(
                model=model,
                tools=tool_instances,
                instructions=agno_config.instructions,
                markdown=agno_config.markdown
            )
            
            # Store agent instance
            self.agents[agent_id]["instance"] = agent
            self.agents[agent_id]["status"] = "running"
            
            # Update database status
            super().update_agent_status(agent_id, "running")
            
            logger.info(f"Started Agno agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Agno agent {agent_id}: {str(e)}")
            self.agents[agent_id]["error"] = str(e)
            super().update_agent_status(agent_id, "error", str(e))
            return False
    
    def _cleanup_agent_resources(self, agent_id: int):
        """Clean up resources for an Agno agent."""
        if agent_id in self.agents and self.agents[agent_id]["instance"]:
            # No special cleanup needed for Agno agents
            self.agents[agent_id]["instance"] = None
            # Update status to stopped
            super().update_agent_status(agent_id, "stopped")
            

    