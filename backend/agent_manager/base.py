"""
Base agent manager module that defines the interface for all agent managers.
"""
import time
from typing import Dict, List, Optional, Any, Union
import logging
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from backend.database import get_db, SessionLocal
from backend.models import AgentModel, CrewAIAgentModel, LangChainAgentModel, AgnoAgentModel
from backend.config import config
from backend.utils.logging import get_logger

# Set up logger
logger = get_logger(__name__)

# Dict for storing running task futures
running_tasks = {}

class BaseAgentManager:
    """
    Base class for all agent managers.
    Defines the common interface and functionality for managing agents.
    """
    def __init__(self):
        self.agents = {}  # Runtime cache of agent instances
        self.executor = ThreadPoolExecutor(max_workers=config.performance.max_workers)
        
        # Initialize in-memory cache from database
        self._load_agents_from_db()
    
    def validate_agent_config(self, config: Dict[str, Any]) -> Union[bool, str]:
        """Validate the given agent configuration."""
        raise NotImplemented("subclass must implement validate_agent_config")

    def get_schema(self) -> Any:
        """
        Get the schema for this agent framework.

        Returns:
            A FrameworkSchema object describing the fields required by this framework.
        """
        raise NotImplementedError("Subclasses must implement get_schema")
    
    def _load_agents_from_db(self):
        """Load existing agents from the database into memory."""
        try:
            db = SessionLocal()
            db_agents = db.query(AgentModel).filter(AgentModel.framework == self.framework_name).all()
            
            for agent in db_agents:
                config = {
                    "name": agent.name,
                    "description": agent.description,
                    "framework": agent.framework,
                    "model": agent.model,
                    "model_config": agent.model_config,
                }
                
                # Add framework-specific configuration
                if agent.framework == "crewai" and agent.crewai_config:
                    # Use the to_dict method for consistent serialization
                    config.update(agent.crewai_config.to_dict())
                elif agent.framework == "langchain" and agent.langchain_config:
                    # Use the to_dict method for consistent serialization
                    config.update(agent.langchain_config.to_dict())
                elif agent.framework == "agno" and agent.agno_config:
                    # Use the to_dict method for consistent serialization
                    config.update(agent.agno_config.to_dict())
                
                self.agents[agent.id] = {
                    "config": config,
                    "status": agent.status,
                    "instance": None,
                    "results": [],
                    "error": agent.error
                }
            
            logger.info(f"Loaded {len(db_agents)} {self.framework_name} agents from database")
            
        except Exception as e:
            logger.error(f"Error loading {self.framework_name} agents from database: {str(e)}")
        finally:
            db.close()
    
    def create_agent(self, config: Dict[str, Any]) -> int:
        """Create a new agent with the given configuration and store in database."""
        try:
            # Set the framework name
            config["framework"] = self.framework_name
            
            # Create database record
            db = SessionLocal()
            
            # Create base agent model
            db_agent = AgentModel(
                name=config["name"],
                description=config.get("description"),
                framework=self.framework_name,
                model=config.get("model"),
                model_config=config.get("model_config"),
                status="stopped"
            )
            db.add(db_agent)
            db.flush()  # Get the ID without committing
            
            # Add framework-specific configuration
            if self.framework_name == "crewai":
                
                # Import here to avoid circular imports
                from backend.agent_manager.agent_providers.crewai.config import CrewAIConfig
                
                # Create config object for better validation and defaults
                crewai_config_obj = CrewAIConfig.from_dict(config)
                
                # Create database model from config object
                crewai_model = CrewAIAgentModel.from_dict(crewai_config_obj.to_dict(), db_agent.id)
                db.add(crewai_model)
                
            elif self.framework_name == "langchain":
                # Import here to avoid circular imports
                from backend.agent_manager.agent_providers.langchain.config import LangChainConfig
                # from backend.agent_manager.agent_providers.langchain.models import LangChainAgentModel
                
                # Create config object for better validation and defaults
                langchain_config_obj = LangChainConfig.from_dict(config)
                
                # Create database model from config object
                langchain_model = LangChainAgentModel.from_dict(langchain_config_obj.to_dict(), db_agent.id)
                db.add(langchain_model)
                
            elif self.framework_name == "agno":
                # Import here to avoid circular imports
                from backend.agent_manager.agent_providers.agno.config import AgnoConfig
                
                # Create config object for better validation and defaults
                agno_config_obj = AgnoConfig.from_dict(config)
                
                # Create database model from config object
                agno_model = AgnoAgentModel.from_dict(agno_config_obj.to_dict(), db_agent.id)
                db.add(agno_model)
            
            db.commit()
            db.refresh(db_agent)
            
            agent_id = db_agent.id
            
            # Store in memory cache
            self.agents[agent_id] = {
                "config": config,
                "status": "stopped",
                "instance": None,
                "results": []
            }
            
            logger.info(f"Created agent {agent_id}: {config.get('name')}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise
        finally:
            db.close()
    
    def start_agent(self, agent_id: int) -> bool:
        """
        Start an agent. To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement start_agent")
    
    def stop_agent(self, agent_id: int) -> bool:
        """
        Stop a running agent and update database.
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False
            
        try:
            if agent_id in running_tasks:
                # Mark it stopped
                self.agents[agent_id]["status"] = "stopped"
            
            # Clean up instances to save memory
            self.agents[agent_id]["instance"] = None
            self._cleanup_agent_resources(agent_id)
                
            self.agents[agent_id]["status"] = "stopped"
            
            # Update database
            db = SessionLocal()
            try:
                db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
                if db_agent:
                    db_agent.status = "stopped"
                    db.commit()
                    logger.info(f"Agent {agent_id} stopped successfully")
            finally:
                db.close()
                
            return True
        
        except Exception as e:
            logger.error(f"Error stopping agent {agent_id}: {str(e)}")
            return False
    
    def _cleanup_agent_resources(self, agent_id: int):
        """
        Clean up any agent-specific resources. To be implemented by subclasses.
        """
        pass
    
    def query_agent(self, agent_id: int, query: str, max_retries: int = 2) -> Dict[str, Any]:
        """Run a query against an agent with retry logic."""
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found for query")
            return {"error": "Agent not found"}
            
        if self.agents[agent_id]["status"] != "running":
            logger.warning(f"Agent {agent_id} not running for query")
            return {"error": "Agent not running. Please start the agent first."}
        
        # Store query in database
        db = SessionLocal()
        try:
            # Record the query attempt in the DB (if we had a query history table)
            pass
        except Exception as e:
            logger.error(f"Error recording query: {str(e)}")
        finally:
            db.close()
        
        retries = 0
        last_error = None
        
        while retries <= max_retries:
            try:
                # Run the query in a separate thread to avoid blocking
                future = self.executor.submit(self._run_query, agent_id, query)
                running_tasks[agent_id] = future
                
                # Wait for the result with timeout
                timeout = config.performance.worker_timeout
                result = future.result(timeout=timeout)
                
                # Store recent results in memory
                self.agents[agent_id]["results"].append({"query": query, "response": result, "timestamp": time.time()})
                if len(self.agents[agent_id]["results"]) > 10:  # Keep only last 10 results
                    self.agents[agent_id]["results"].pop(0)
                
                # Success! Return the result
                return {"response": result}
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Error querying agent {agent_id} (attempt {retries+1}): {last_error}")
                retries += 1
                
                # If we have more retries, wait a bit before trying again
                if retries <= max_retries:
                    time.sleep(1)  # Wait 1 second between retries
                
            finally:
                # Clean up the task reference
                if agent_id in running_tasks:
                    del running_tasks[agent_id]
        
        # If we got here, all retries failed
        logger.error(f"All retries failed for query to agent {agent_id}")
        return {"error": f"Error executing query after {max_retries+1} attempts: {last_error}"}
    
    def _run_query(self, agent_id: int, query: str) -> str:
        """Execute the query. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _run_query")
    
    def get_agent_status(self, agent_id: int) -> Dict[str, Any]:
        """Get the current status of an agent."""
        if agent_id not in self.agents:
            return {"error": "Agent not found"}
            
        agent_data = self.agents[agent_id]
        return {
            "status": agent_data["status"],
            "results": agent_data.get("results", []),
            "error": agent_data.get("error", None)
        }
        
    def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent from the database and memory."""
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found for deletion")
            return False

        try:
            # First, make sure the agent is stopped
            if self.agents[agent_id]["status"] == "running":
                self.stop_agent(agent_id)
            
            # Remove from database
            db = SessionLocal()
            db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            if not db_agent:
                logger.warning(f"Agent {agent_id} not found in database")
                return False
                
            # Delete the agent from database
            db.delete(db_agent)
            db.commit()
            
            # Clean up any resources and remove from memory cache
            self._cleanup_agent_resources(agent_id)
            if agent_id in self.agents:
                del self.agents[agent_id]
            
            logger.info(f"Agent {agent_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting agent {agent_id}: {str(e)}")
            return False
        finally:
            db.close()

    def update_agent(self, agent_id: int, config: Dict[str, Any]) -> bool:
        """Update an existing agent with the given configuration and store in database."""
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found for update")
            return False

        try:
            # Set the framework name (don't allow changing framework)
            config["framework"] = self.framework_name
            
            # Update database record
            db = SessionLocal()
            db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            if not db_agent:
                logger.warning(f"Agent {agent_id} not found in database")
                return False
                
            # Update base fields
            db_agent.name = config.get("name", db_agent.name)
            db_agent.description = config.get("description", db_agent.description)
            db_agent.model = config.get("model", db_agent.model)
            db_agent.model_config = config.get("model_config", db_agent.model_config)
            
            # Update framework-specific fields
            if self.framework_name == "crewai":
                # Import here to avoid circular imports
                from backend.agent_manager.agent_providers.crewai.config import CrewAIConfig
                
                # Create config object with current values merged with new values
                current_config = {}
                if db_agent.crewai_config:
                    current_config = db_agent.crewai_config.to_dict()
                
                # Merge with new config values
                merged_config = {**current_config, **config}
                crewai_config_obj = CrewAIConfig.from_dict(merged_config)
                
                # Update or create the model
                if not db_agent.crewai_config:
                    db_agent.crewai_config = CrewAIAgentModel.from_dict(crewai_config_obj.to_dict(), agent_id)
                else:
                    # Update fields individually to preserve the existing record
                    db_agent.crewai_config.role = crewai_config_obj.role
                    db_agent.crewai_config.backstory = crewai_config_obj.backstory
                    db_agent.crewai_config.task = crewai_config_obj.task
                    db_agent.crewai_config.goals = crewai_config_obj.goals
                    db_agent.crewai_config.tools = crewai_config_obj.tools
                    db_agent.crewai_config.memory_enabled = crewai_config_obj.memory_enabled
                    db_agent.crewai_config.expected_output = crewai_config_obj.expected_output
                
            elif self.framework_name == "langchain":
                # Import here to avoid circular imports
                from backend.agent_manager.agent_providers.langchain.config import LangChainConfig
                # from backend.agent_manager.agent_providers.langchain.models import LangChainAgentModel
                
                # Create config object with current values merged with new values
                current_config = {}
                if db_agent.langchain_config:
                    current_config = db_agent.langchain_config.to_dict()
                
                # Merge with new config values
                merged_config = {**current_config, **config}
                langchain_config_obj = LangChainConfig.from_dict(merged_config)
                
                # Update or create the model
                if not db_agent.langchain_config:
                    db_agent.langchain_config = LangChainAgentModel.from_dict(langchain_config_obj.to_dict(), agent_id)
                else:
                    # Update fields individually to preserve the existing record
                    db_agent.langchain_config.agent_type = langchain_config_obj.agent_type
                    db_agent.langchain_config.tools = langchain_config_obj.tools
                    db_agent.langchain_config.memory_type = langchain_config_obj.memory_type
                    db_agent.langchain_config.verbose = langchain_config_obj.verbose
                    db_agent.langchain_config.chain_type = langchain_config_obj.chain_type
                    
            elif self.framework_name == "agno":
                # Import here to avoid circular imports
                from backend.agent_manager.agent_providers.agno.config import AgnoConfig
                
                # Create config object with current values merged with new values
                current_config = {}
                if db_agent.agno_config:
                    current_config = db_agent.agno_config.to_dict()
                
                # Merge with new config values
                merged_config = {**current_config, **config}
                agno_config_obj = AgnoConfig.from_dict(merged_config)
                
                # Update or create the model
                if not db_agent.agno_config:
                    db_agent.agno_config = AgnoAgentModel.from_dict(agno_config_obj.to_dict(), agent_id)
                else:
                    # Update fields individually to preserve the existing record
                    db_agent.agno_config.model_id = agno_config_obj.model_id
                    db_agent.agno_config.tools = agno_config_obj.tools
                    db_agent.agno_config.instructions = agno_config_obj.instructions
                    db_agent.agno_config.markdown = agno_config_obj.markdown
                    db_agent.agno_config.stream = agno_config_obj.stream
            
            db.commit()
            
            # Update memory cache with framework-specific config
            cache_config = {
                "name": db_agent.name,
                "description": db_agent.description,
                "framework": db_agent.framework,
                "model": db_agent.model,
                "model_config": db_agent.model_config,
            }
            
            if self.framework_name == "crewai" and db_agent.crewai_config:
                # Use the to_dict method for consistent serialization
                cache_config.update(db_agent.crewai_config.to_dict())
            elif self.framework_name == "langchain" and db_agent.langchain_config:
                # Use the to_dict method for consistent serialization
                cache_config.update(db_agent.langchain_config.to_dict())
            elif self.framework_name == "agno" and db_agent.agno_config:
                # Use the to_dict method for consistent serialization
                cache_config.update(db_agent.agno_config.to_dict())
            
            self.agents[agent_id]["config"] = cache_config
            
            # If agent was running, may need to restart
            was_running = self.agents[agent_id]["status"] == "running"
            if was_running:
                self.stop_agent(agent_id)
                self.start_agent(agent_id)
            
            logger.info(f"Updated agent {agent_id}: {config.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating agent: {str(e)}")
            return False
        finally:
            db.close()

    def get_all_agents(self) -> Dict[int, Dict[str, Any]]:
        """Get information about all agents from database."""
        try:
            db = SessionLocal()
            db_agents = db.query(AgentModel).filter(AgentModel.framework == self.framework_name).all()
            
            results = {}
            for agent in db_agents:
                result = {
                    "id": agent.id,
                    "name": agent.name,
                    "description": agent.description,
                    "framework": agent.framework,
                    "status": agent.status,
                    "model": agent.model,
                    "created_at": agent.created_at.isoformat() if agent.created_at else None,
                }
                
                # Add framework-specific fields
                if agent.framework == "crewai" and agent.crewai_config:
                    # Use the to_dict method for consistent serialization
                    result.update(agent.crewai_config.to_dict())
                elif agent.framework == "langchain" and agent.langchain_config:
                    # Use the to_dict method for consistent serialization
                    result.update(agent.langchain_config.to_dict())
                elif agent.framework == "agno" and agent.agno_config:
                    # Use the to_dict method for consistent serialization
                    result.update(agent.agno_config.to_dict())
                    
                # Use the AgentModel to_dict method
                results[agent.id] = agent.to_dict()
                
                # Ensure runtime cache is in sync
                if agent.id not in self.agents:
                    # Use the AgentModel to_dict method for the config
                    self.agents[agent.id] = {
                        "config": agent.to_dict(),
                        "status": agent.status,
                        "instance": None,
                        "results": []
                    }
                
            return results
        
        except Exception as e:
            logger.error(f"Error getting all agents: {str(e)}")
            return {}
        finally:
            db.close()
    
    def update_agent_status(self, agent_id: int, status: str, error: str = None):
        """Update agent status in the database."""
        from backend.database import SessionLocal
        
        try:
            db = SessionLocal()
            db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            if db_agent:
                db_agent.status = status
                if error:
                    db_agent.error = error
                db.commit()
        except Exception as e:
            logger.error(f"Error updating agent status: {str(e)}")
        finally:
            db.close()
    
    @property
    def framework_name(self) -> str:
        """Return the name of the framework this manager handles."""
        raise NotImplementedError("Subclasses must implement framework_name property")
