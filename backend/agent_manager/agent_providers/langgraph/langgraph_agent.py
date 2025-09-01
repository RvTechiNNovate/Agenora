import time
from typing import List

from langgraph.prebuilt import create_react_agent
from backend.database import SessionLocal
from backend.models import AgentModel, LanggraphAgentModel
from backend.utils.logging import get_logger
from backend.schemas import FrameworkSchema
from typing import Dict, List, Optional, Any, Union
from backend.agent_manager.base import BaseAgentManager
from backend.llm_providers.manager import llm_provider_manager
from sqlalchemy.orm import Session
from .config import LanggraphConfig
# Set up logger
logger = get_logger(__name__)

class LanggraphManager(BaseAgentManager):
    def __init__(self):
        self.tools = {}
        super().__init__()
    
    @property
    def framework_name(self) -> str:
        return "langgraph"

    def get_schema(self) -> Any:
        """Get the schema for Langraph framework."""
        return FrameworkSchema(
            name="Langraph",
            description="Framework for building applications with LLMs",
            fields={
                "prompt": str,
                "tools": List[str],
             
            }
        )

    def validate_agent_config(self, config: dict) -> bool:
        required_fields = ["prompt", "tools"]
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field: {field}")
                return f"Missing required field: {field}"
        
        logger.info("Agent config validated successfully")
        # Implement validation logic for the agent config
        return True
    
    def start_agent(self, agent_id):
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found in cache")
            return False
            
        if self.agents[agent_id]["status"] == "running":
            logger.info(f"Agent {agent_id} already running")
            return True  # Already running
            
        # try:
        # Get agent config from cache
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
        
        # Create default tools (can be customized based on agent type)
        tools = []

        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=config.get("prompt"),
        )
        # Store the agent instance
        self.agents[agent_id]["instance"] = agent
        self.agents[agent_id]["status"] = "running"
        
        # Update database
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

    def _run_query(self, agent_id: int, query: str):
        """Execute the query using LangChain (meant to run in a separate thread)."""
        start_time = time.time()
        logger.info(f"Running query for agent {agent_id}: {query[:50]}...")
        
        try:
            agent = self.agents[agent_id]["instance"]
            if not agent:
                logger.error(f"Agent {agent_id} instance not found")
                return "Error: Agent not initialized"
            response = agent.invoke({"messages": [{"role": "user", "content": query}]})
            print(response.get('messages')[-1].content)
            logger.info(f"Query completed in {time.time() - start_time:.2f} seconds")
            return response.get('messages')[-1].content
        except Exception as e:
            logger.error(f"Error occurred while running query for agent {agent_id}: {e}")
            return "Error: Query execution failed"

    def _cleanup_agent_resources(self, agent_id):
        """Clean up langgraph specific resources."""
        if agent_id in self.tools:
            del self.tools[agent_id]
        # Update status to stopped
        super().update_agent_status(agent_id, "stopped")
    
    def _create_framework_config(self, db: Session, db_agent: AgentModel, config: Dict[str, Any]) -> None:
        """
        Create framework-specific configuration for the agent.
        
        Args:
            db: Database session
            db_agent: Agent model instance
            config: Agent configuration
        """
        # Create config object for better validation and defaults
        langgraph_config_obj = LanggraphConfig.from_dict(config)
        
        # Create database model
        langgraph_model = LanggraphAgentModel.from_dict(langgraph_config_obj.to_dict(), db_agent.id)
        db.add(langgraph_model)
    
    def _get_framework_config(self, agent: AgentModel) -> Dict[str, Any]:
        """
        Get framework-specific configuration for the agent.
        
        Args:
            agent: Agent model instance
            
        Returns:
            Dictionary containing framework-specific configuration
        """
        if agent.langgraph_config:
            return agent.langgraph_config.to_dict()
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
        if not db_agent.langgraph_config:
            error_msg = f"Agent {db_agent.id} does not have LangGraph configuration"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Get current config values
        current_config = db_agent.langgraph_config.to_dict()
        
        # Merge with new config values
        merged_config = {**current_config, **config}
        langgraph_config_obj = LanggraphConfig.from_dict(merged_config)
        
        # Update fields individually to preserve the existing record
        db_agent.langgraph_config.tools = langgraph_config_obj.tools
        db_agent.langgraph_config.prompt = langgraph_config_obj.prompt
        
manager = LanggraphManager()