from crewai import Agent, Task, Crew
import os
import time
from typing import Dict, List, Optional, Any, Union
from backend.database import SessionLocal
from backend.models import AgentModel, CrewAIAgentModel
from backend.utils.logging import get_logger
from backend.config import config
from backend.agent_manager.base import BaseAgentManager, running_tasks
from backend.llm_providers.manager import llm_provider_manager

# Set up logger
logger = get_logger(__name__)

class CrewAIManager(BaseAgentManager):
    def __init__(self):
        self.crews = {}   # Runtime cache of crew instances
        super().__init__()
    
    @property
    def framework_name(self) -> str:
        """Return the name of the framework this manager handles."""
        return "crewai"
    
    def get_schema(self) -> Any:
        """Get the schema for CrewAI framework."""
        from backend.schemas import FrameworkSchema
        from typing import List
        
        return FrameworkSchema(
            name="CrewAI",
            description="Multi-agent framework for creating agent teams",
            fields={
                "role": str,
                "backstory": str,
                "task": str,
                "expected_output": str
            }
        )
        
    def _cleanup_agent_resources(self, agent_id: int):
        """Clean up CrewAI specific resources."""
        if agent_id in self.crews:
            del self.crews[agent_id]
        # Update status to stopped
        super().update_agent_status(agent_id, "stopped")
    
    def start_agent(self, agent_id: int) -> bool:
        """Start an agent by creating its CrewAI instance and update database."""        
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
            model_name = config.get("model")
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
            
            # Create CrewAI agent
            agent = Agent(
                role=config.get("role"),
                goal=config.get("description"),
                backstory=config.get("backstory"),
                verbose=True,
                llm=llm
            )
            
            # Create a task for this agent
            task = Task(
                description=config.get("task"),
                agent=agent,
                expected_output=config.get("expected_output")
            )
            
            # Create a crew with this agent
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True
            )
            
            # Store instances in memory
            self.agents[agent_id]["instance"] = agent
            self.crews[agent_id] = crew
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
        
        except Exception as e:
            error_msg = f"Error starting agent {agent_id}: {str(e)}"
            logger.error(error_msg)
            
            # Update memory cache
            self.agents[agent_id]["error"] = str(e)
            
            # Update database
            db = SessionLocal()
            try:
                db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
                if db_agent:
                    db_agent.error = str(e)
                    db.commit()
            finally:
                db.close()
                
            return False
        
    def query_agent(self, agent_id: int, query: str, max_retries: int = 2) -> Dict[str, Any]:
        """Run a query against a CrewAI agent with retry logic."""
        # Add CrewAI specific validation
        if agent_id not in self.crews:
            logger.warning(f"Agent {agent_id} crew not initialized")
            return {"error": "Agent crew not initialized"}
            
        # Use the base class implementation for the actual query execution
        return super().query_agent(agent_id, query, max_retries)
    
    def _run_query(self, agent_id: int, query: str) -> str:
        """Execute the query using CrewAI (meant to run in a separate thread)."""
        start_time = time.time()
        logger.info(f"Running query for agent {agent_id}: {query[:50]}...")
        
        try:
            crew = self.crews.get(agent_id)
            if not crew:
                logger.error(f"Agent {agent_id} crew not found")
                return "Error: Agent crew not initialized"
            
            # For a single agent, we need to create a task with the query
            agent = self.agents[agent_id]["instance"]
            if not agent:
                logger.error(f"Agent {agent_id} instance not found")
                return "Error: Agent not initialized"
                
            # Create a new task with the query
            task = Task(
                description=query,
                agent=agent,
                expected_output="A helpful and comprehensive response to the user's query"
            )
            
            # Create a temporary crew with this task
            temp_crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False  # Reduce verbosity for queries
            )
            
            # Execute the task
            logger.info(f"Executing task for agent {agent_id}")
            result = temp_crew.kickoff()
            logger.info(f"Usage: {result.token_usage}")

            # Log completion
            duration = time.time() - start_time
            logger.info(f"Query for agent {agent_id} completed in {duration:.2f} seconds")
            
            return str(result)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error in _run_query for agent {agent_id} after {duration:.2f} seconds: {str(e)}")
            
            # Return a user-friendly error message
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
            
    def validate_agent_config(self, config: Dict[str, Any]) -> Union[bool, str]:
        """Validate CrewAI agent configuration."""
        required_fields = ["role", "task", "model","expected_output","backstory"]
        for field in required_fields:
            if field not in config:
                logger.error(f"Validation failed: Missing field {field}")
                return f"Missing required field: {field}"
        for field in required_fields:
            if not config[field]:
                logger.error(f"Validation failed: Empty field {field}")
                return f"Field '{field}' cannot be empty"
        # Additional validation can be added here
        logger.info("CrewAI agent configuration validated successfully")
        return True


# Singleton instance
manager = CrewAIManager()
