"""
LangChain agent manager module.
"""
from langchain.agents import initialize_agent, AgentType

import os
import time
from typing import List
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from backend.db.repository import db_repository
from backend.schemas.schemas import FrameworkSchema
from backend.db.models import AgentModel, LangChainAgentModel
from backend.core.logging import get_logger
from backend.agent_manager.base import BaseAgentManager
from backend.llm_manager.manager import llm_provider_manager
from backend.agent_manager.providers.langchain.config import LangChainConfig


# Set up logger
logger = get_logger(__name__)

class LangChainManager(BaseAgentManager):
    """
    Manager for LangChain agents.
    """
    def __init__(self):
        self.tools = {}  # Runtime cache of agent tools
        super().__init__()
    
    @property
    def framework_name(self) -> str:
        """Return the name of the framework this manager handles."""
        return "langchain"
    
    def get_schema(self) -> Any:
        """Get the schema for LangChain framework."""
        
        return FrameworkSchema(
            name="LangChain",
            description="Framework for building applications with LLMs",
            fields={
                "agent_type": str,
                "tools": List[str]
            }
        )
        
    def validate_agent_config(self, config: Dict[str, Any]) -> Union[bool, str]:
        """Validate LangChain agent configuration."""
        # Check required fields
        required_fields = ["agent_type", "model"]
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field: {field}")
                return f"Missing required field: {field}"
        
        # Validate agent_type is one of the allowed values
        valid_agent_types = ["conversational", "zero-shot-react-description", "react-docstore", "structured-chat"]
        if config["agent_type"] not in valid_agent_types:
            logger.error(f"Invalid agent_type: {config['agent_type']}")
            return f"Invalid agent_type: {config['agent_type']}. Must be one of: {', '.join(valid_agent_types)}"
            
        # Validate tools is a list
        if "tools" in config and not isinstance(config["tools"], list):
            logger.error("Tools must be a list")
            return "Tools must be a list"
            
        # If we got here, configuration is valid
        logger.info("LangChain agent configuration validated successfully")
        return True
    
    def _cleanup_agent_resources(self, agent_id: int):
        """Clean up LangChain specific resources."""
        if agent_id in self.tools:
            del self.tools[agent_id]
        # Update status to stopped
        db_repository.agents.update_agent_status(agent_id, "stopped")
        
    def _create_framework_config(self, db: Session, db_agent: AgentModel, config: Dict[str, Any]) -> None:
        """
        Create framework-specific configuration for the agent.
        
        Args:
            db: Database session
            db_agent: Agent model instance
            config: Agent configuration
        """
        # Create config object for better validation and defaults
        langchain_config_obj = LangChainConfig.from_dict(config)
        
        # Create database model from config object
        langchain_model = LangChainAgentModel.from_dict(langchain_config_obj.to_dict(), db_agent.id)
        db.add(langchain_model)
        
    def _get_framework_config(self, agent: AgentModel) -> Dict[str, Any]:
        """
        Get framework-specific configuration for the agent.
        
        Args:
            agent: Agent model instance
            
        Returns:
            Dictionary containing framework-specific configuration
        """
        if agent.langchain_config:
            return agent.langchain_config.to_dict()
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
        if not db_agent.langchain_config:
            error_msg = f"Agent {db_agent.id} does not have LangChain configuration"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Get current config values
        current_config = db_agent.langchain_config.to_dict()
        
        # Merge with new config values
        merged_config = {**current_config, **config}
        langchain_config_obj = LangChainConfig.from_dict(merged_config)
        
        # Update fields individually to preserve the existing record
        db_agent.langchain_config.agent_type = langchain_config_obj.agent_type
        db_agent.langchain_config.tools = langchain_config_obj.tools
        db_agent.langchain_config.memory_type = langchain_config_obj.memory_type
        db_agent.langchain_config.verbose = langchain_config_obj.verbose
        db_agent.langchain_config.chain_type = langchain_config_obj.chain_type
    
    def start_agent(self, agent_id: int) -> bool:
        """Start a LangChain agent by creating its instance and update database."""        
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found in cache")
            return False
            
        if self.agents[agent_id]["status"] == "running":
            logger.info(f"Agent {agent_id} already running")
            return True  # Already running
            
        try:
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
            
            # Set up memory for the agent
            # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            
            # Create default tools (can be customized based on agent type)
            tools = []
            
            # Create the LangChain agent
            agent_type = AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=agent_type,
                # memory=memory,
                verbose=True,
                handle_parsing_errors=True
            )
            
            # Store the agent instance
            self.agents[agent_id]["instance"] = agent
            self.agents[agent_id]["status"] = "running"
            
            db_repository.agents.update_agent_status(agent_id, "running")
                
            return True
        
        except Exception as e:
            error_msg = f"Error starting agent {agent_id}: {str(e)}"
            logger.error(error_msg)
            
            # Update memory cache
            self.agents[agent_id]["error"] = str(e)
            
            # Update database
            db_repository.agents.update_agent_status(agent_id, "error", error=str(e))
                
            return False
    
    def _run_query(self, agent_id: int, query: str) -> str:
        """Execute the query using LangChain (meant to run in a separate thread)."""
        start_time = time.time()
        logger.info(f"Running query for agent {agent_id}: {query[:50]}...")
        
        try:
            agent = self.agents[agent_id]["instance"]
            if not agent:
                logger.error(f"Agent {agent_id} instance not found")
                return "Error: Agent not initialized"
            
            # Execute the query with the LangChain agent
            result = agent.invoke(query)
            
            # Log completion
            duration = time.time() - start_time
            logger.info(f"Query for agent {agent_id} completed in {duration:.2f} seconds")
            
            return str(result)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error in _run_query for agent {agent_id} after {duration:.2f} seconds: {str(e)}")
            
            # Return a user-friendly error message
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
            
            
# Singleton instance
manager = LangChainManager()
