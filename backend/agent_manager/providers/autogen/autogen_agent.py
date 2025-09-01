from typing import Dict, Any, Optional, List, Union
from backend.agent_manager.base import BaseAgentManager
from backend.db.session import SessionLocal
from backend.db.models import AgentModel
from backend.core.logging import get_logger
from backend.llm_manager.manager import llm_provider_manager
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

# Set up logger
logger = get_logger(__name__)

class AutoGenManager(BaseAgentManager):
    """Manager for AutoGen agents."""
    
    def __init__(self):
        """Initialize the AutoGen manager."""
        super().__init__()
    
    @property
    def framework_name(self) -> str:
        """Return the name of the framework this manager handles."""
        return "autogen"  # Replace with your framework's name
    
    def get_schema(self) -> Any:
        """Get the schema for this framework."""
        from backend.schemas.schemas import FrameworkSchema
        from typing import List
        
        return FrameworkSchema(
            name="AutoGen Framework",  # User-friendly name
            description="Description of the AutoGen framework",
            fields={
                # Define the fields specific to your framework
                "system_message": str, 
            }
        )
    
    def validate_agent_config(self, config: Dict[str, Any]) -> Union[bool, str]:
        """Validate the configuration for this framework."""
        # Check required fields
        required_fields = ["system_message"]
        for field in required_fields:
            if field not in config:
                return f"Missing required field: {field}"
        
        # Add additional validation logic specific to your framework
        
        # If valid, return True
        return True
    
    def _run_query(self, agent_id: int, query: str) -> str:
        """Execute a query with an agent."""
        # Implement query execution logic for your framework
        pass
    
    def start_agent(self, agent_id: int) -> bool:
        """Start an agent."""
        # Implement agent startup logic for your framework
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found in cache")
            return False
            
        if self.agents[agent_id]["status"] == "running":
            logger.info(f"Agent {agent_id} already running")
            return True  # Already running
            
        
        config = self.agents[agent_id]["config"]
        
        # Set up language model
        model_name = config.get("model", "gpt-3.5-turbo")
        model_config = config.get("model_config", {})
        temperature = float(model_config.get("temperature", 0.7))
        max_tokens = model_config.get("max_tokens")
        
        # Parse provider from model string if specified (e.g. "azure:gpt-4")
        provider_name = None
        if ":" in model_name:
            parts = model_name.split(":", 1)
            provider_name, model_name = parts
        
        # Get LLM from provider manager
        llm = llm_provider_manager.get_llm(
            provider_name=provider_name,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        
        if not llm:
            raise ValueError(f"Could not initialize LLM for model {model_name}")
        
        agent = AssistantAgent(
            name=config.get("name"),
            model_client=llm, 
            system_message=TextMessage(
                content=config.get("system_message")
                ),
            tools=[],  
            )
        
        self.agents[agent_id]["instance"] = agent
        self.agents[agent_id]["status"] = "running"
        
        db = SessionLocal()
        try:
            db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            if db_agent:
                db_agent.status = "running"
                db_agent.error = None
                db.commit()
                logger.info(f"Agent {agent_id} started successfully")
        finally:
            db.close()
            
        return True

    def _cleanup_agent_resources(self, agent_id):
        """Clean up LangChain specific resources."""
        if agent_id in self.tools:
            del self.tools[agent_id]
        # Update status to stopped
        super().update_agent_status(agent_id, "stopped")

manager = AutoGenManager()