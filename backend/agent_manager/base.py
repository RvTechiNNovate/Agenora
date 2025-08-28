"""
Base agent manager module that defines the interface for all agent managers.
"""
import time
from typing import Dict, List, Optional, Any, Union
import logging
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from backend.database import AgentModel, get_db, SessionLocal
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
    
    def _load_agents_from_db(self):
        """Load existing agents from the database into memory."""
        try:
            db = SessionLocal()
            db_agents = db.query(AgentModel).filter(AgentModel.framework == self.framework_name).all()
            
            for agent in db_agents:
                self.agents[agent.id] = {
                    "config": {
                        "name": agent.name,
                        "description": agent.description,
                        "framework": agent.framework,
                        "role": agent.role,
                        "backstory": agent.backstory,
                        "task": agent.task,
                        "model": agent.model,
                        "model_config": agent.model_config,
                    },
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
            db_agent = AgentModel.from_dict(config)
            db.add(db_agent)
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
                
            # Update fields
            db_agent.name = config.get("name", db_agent.name)
            db_agent.description = config.get("description", db_agent.description)
            db_agent.role = config.get("role", db_agent.role)
            db_agent.backstory = config.get("backstory", db_agent.backstory)
            db_agent.task = config.get("task", db_agent.task)
            db_agent.model = config.get("model", db_agent.model)
            db_agent.model_config = config.get("model_config", db_agent.model_config)
            
            db.commit()
            
            # Update memory cache
            self.agents[agent_id]["config"] = {
                "name": db_agent.name,
                "description": db_agent.description,
                "framework": db_agent.framework,
                "role": db_agent.role,
                "backstory": db_agent.backstory,
                "task": db_agent.task,
                "model": db_agent.model,
                "model_config": db_agent.model_config,
            }
            
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
                results[agent.id] = {
                    "id": agent.id,
                    "name": agent.name,
                    "description": agent.description,
                    "framework": agent.framework,
                    "status": agent.status,
                    "model": agent.model,
                    "created_at": agent.created_at.isoformat() if agent.created_at else None,
                }
                
                # Ensure runtime cache is in sync
                if agent.id not in self.agents:
                    self.agents[agent.id] = {
                        "config": {
                            "name": agent.name,
                            "description": agent.description,
                            "framework": agent.framework,
                            "role": agent.role,
                            "backstory": agent.backstory,
                            "task": agent.task,
                            "model": agent.model,
                            "model_config": agent.model_config,
                        },
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

    @property
    def framework_name(self) -> str:
        """Return the name of the framework this manager handles."""
        raise NotImplementedError("Subclasses must implement framework_name property")
