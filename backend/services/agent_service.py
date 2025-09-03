"""
Agent service module for business logic related to agent operations.
"""
from typing import Dict, Any, Optional, List
from backend.core.logging import get_logger
from backend.db.repository import db_repository
from backend.agent_manager.manager import agent_provider_manager

logger = get_logger(__name__)


class AgentService:
    """Service class for agent-related business operations."""
    
    @staticmethod
    def start_agent(agent_id: int) -> Dict[str, Any]:
        """
        Start an agent by ID.
        
        Args:
            agent_id: ID of the agent to start
            
        Returns:
            Dict containing success status and message
        """
        try:
            # Get agent from database
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }
            
            # Get the appropriate provider
            provider = agent_provider_manager.get_provider(agent.framework)
            if not provider:
                return {
                    "success": False,
                    "error": f"Framework {agent.framework} not supported",
                    "status_code": 404
                }
            
            # Start the agent
            success = provider.start_agent(agent_id)
            
            if success:
                logger.info(f"Agent {agent_id} started successfully")
                return {
                    "success": True,
                    "status": "started",
                    "message": f"Agent {agent_id} started successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to start agent",
                    "status_code": 500
                }
                
        except Exception as e:
            logger.error(f"Error starting agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Internal error starting agent: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def stop_agent(agent_id: int) -> Dict[str, Any]:
        """
        Stop an agent by ID.
        
        Args:
            agent_id: ID of the agent to stop
            
        Returns:
            Dict containing success status and message
        """
        try:
            # Get agent from database
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }
            
            # Get the appropriate provider
            provider = agent_provider_manager.get_provider(agent.framework)
            if not provider:
                return {
                    "success": False,
                    "error": f"Framework {agent.framework} not supported",
                    "status_code": 404
                }
            
            # Stop the agent
            success = provider.stop_agent(agent_id)
            
            if success:
                logger.info(f"Agent {agent_id} stopped successfully")
                return {
                    "success": True,
                    "status": "stopped",
                    "message": f"Agent {agent_id} stopped successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to stop agent",
                    "status_code": 500
                }
                
        except Exception as e:
            logger.error(f"Error stopping agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Internal error stopping agent: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def query_agent(agent_id: int, query: str, max_query_length: int = 100) -> Dict[str, Any]:
        """
        Send a query to an agent.
        
        Args:
            agent_id: ID of the agent to query
            query: Query string to send
            max_query_length: Maximum allowed query length
            
        Returns:
            Dict containing query result or error
        """
        try:
            # Validate query length
            if len(query) > max_query_length:
                return {
                    "success": False,
                    "error": f"Query too long. Maximum length is {max_query_length} characters.",
                    "status_code": 400
                }
            
            # Get agent from database
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }
            
            # Get the appropriate provider
            provider = agent_provider_manager.get_provider(agent.framework)
            if not provider:
                return {
                    "success": False,
                    "error": f"Framework {agent.framework} not supported",
                    "status_code": 404
                }
            
            # Query the agent
            result = provider.query_agent(agent_id, query)
            
            # Handle provider response
            if "error" in result:
                error_msg = result["error"]
                if "not found" in error_msg.lower():
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": 404
                    }
                elif "not running" in error_msg.lower():
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": 400
                    }
                else:
                    return {
                        "success": False,
                        "error": error_msg,
                        "status_code": 500
                    }
            
            # Successful query
            logger.info(f"Query to agent {agent_id} completed successfully")
            return {
                "success": True,
                "response": result.get("response", ""),
                "message": "Query completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error querying agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Internal error querying agent: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def get_agent_status(agent_id: int) -> Dict[str, Any]:
        """
        Get the status of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dict containing agent status information
        """
        try:
            # Get agent from database
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }
            
            # Get the appropriate provider
            provider = agent_provider_manager.get_provider(agent.framework)
            if not provider:
                return {
                    "success": False,
                    "error": f"Framework {agent.framework} not supported",
                    "status_code": 404
                }
            
            # Get agent status
            status_info = provider.get_agent_status(agent_id)
            
            if "error" in status_info:
                return {
                    "success": False,
                    "error": status_info["error"],
                    "status_code": 404
                }
            
            return {
                "success": True,
                "status": status_info.get("status", "unknown"),
                "results": status_info.get("results", []),
                "error": status_info.get("error", None)
            }
            
        except Exception as e:
            logger.error(f"Error getting agent status {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Internal error getting agent status: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def create_agent(agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new agent with the given configuration.
        
        Args:
            agent_data: Dictionary containing agent configuration
            
        Returns:
            Dict containing success status and agent details
        """
        try:
            # Validate framework first
            if "framework" not in agent_data:
                return {
                    "success": False,
                    "error": "Framework must be specified",
                    "status_code": 400
                }
            
            framework = agent_data.get("framework").lower()
            
            # Validate common required fields
            required_fields = ["name", "description", "model"]
            for field in required_fields:
                if field not in agent_data or not agent_data[field]:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}",
                        "status_code": 400
                    }
            
            # Get the appropriate provider
            provider = agent_provider_manager.get_provider(framework)
            if not provider:
                return {
                    "success": False,
                    "error": f"Framework {framework} not supported",
                    "status_code": 404
                }
            
            # Prepare data for manager
            task_dict = agent_data.copy()
            
            # Handle model_settings -> model_config conversion
            if task_dict.get("model_settings"):
                task_dict["model_config"] = task_dict.pop("model_settings")
            
            # TODO: Handle framework-specific fields
            if framework == "crewai":
                task_dict["expected_output"] = agent_data.get("expected_output", "Sort response")
            
            # Validate agent configuration
            if hasattr(provider, 'validate_agent_config'):
                validation_result = provider.validate_agent_config(task_dict)
                if validation_result is not True:
                    return {
                        "success": False,
                        "error": f"Invalid agent configuration: {validation_result}",
                        "status_code": 400
                    }
            
            # Create agent using provider
            agent_id = provider.create_agent(task_dict)
            
            logger.info(f"Created agent {agent_id} with name {task_dict['name']}")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent": {
                    "id": agent_id,
                    "name": task_dict["name"],
                    "description": task_dict["description"],
                    "framework": task_dict["framework"],
                    "status": "stopped",
                    "model": task_dict["model"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create agent: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def get_all_agents() -> Dict[str, Any]:
        """
        Get all agents from all frameworks.
        
        Returns:
            Dict containing all agents
        """
        try:
            all_agents = {}
            
            # Get agents from all framework providers
            for framework, provider in agent_provider_manager.providers.items():
                framework_agents = provider.get_all_agents()
                all_agents.update(framework_agents)
            
            return {
                "success": True,
                "agents": all_agents
            }
            
        except Exception as e:
            logger.error(f"Error getting all agents: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get agents: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def get_agent_by_id(agent_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific agent.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Dict containing agent details
        """
        try:
            # Get agent from database
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }
            
            return {
                "success": True,
                "agent": agent.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get agent: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def update_agent(agent_id: int, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing agent.
        
        Args:
            agent_id: ID of the agent to update
            agent_data: Updated agent configuration
            
        Returns:
            Dict containing success status and updated agent details
        """
        try:
            # Get agent from database
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }
            
            # Validate common fields
            for field in ["name", "description"]:
                if field in agent_data and not agent_data[field]:
                    return {
                        "success": False,
                        "error": f"Field cannot be empty: {field}",
                        "status_code": 400
                    }
            
            # Get framework (use existing or from update data)
            framework = agent_data.get("framework") or agent.framework
            
            # Get the appropriate provider
            provider = agent_provider_manager.get_provider(framework)
            if not provider:
                return {
                    "success": False,
                    "error": f"Framework {framework} not supported",
                    "status_code": 404
                }
            
            # Create version before updating
            current_version = agent.version
            success = db_repository.agents.create_agent_version(agent, current_version)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to create version backup",
                    "status_code": 500
                }

            # Prepare update data
            task_dict = agent_data.copy()

            # Handle model_settings -> model_config conversion
            if task_dict.get("model_settings"):
                task_dict["model_config"] = task_dict.pop("model_settings")

            # Validate configuration if provider supports it
            if hasattr(provider, 'validate_agent_config'):
                current_config = agent.to_dict()
                merged_config = {**current_config, **task_dict}
                validation_result = provider.validate_agent_config(merged_config)
                if validation_result is not True:
                    return {
                        "success": False,
                        "error": f"Invalid agent configuration: {validation_result}",
                        "status_code": 400
                    }

            # Update the agent
            provider_success = provider.update_agent(agent_id, task_dict)

            if provider_success:
                # Update version number
                db_success = db_repository.agents.update_agent(agent_id, {"version": current_version + 1})
                if not db_success:
                    return {
                        "success": False,
                        "error": "Failed to update agent version",
                        "status_code": 500
                    }

                # Get final agent state
                final_agent = db_repository.agents.get_agent_by_id(agent_id)

                logger.info(f"Updated agent {agent_id}")
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "agent": final_agent.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update agent",
                    "status_code": 500
                }
            
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to update agent: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def delete_agent(agent_id: int) -> Dict[str, Any]:
        """
        Delete an agent.
        
        Args:
            agent_id: ID of the agent to delete
            
        Returns:
            Dict containing success status and message
        """
        try:
            # Get agent from database
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }
            
            # Get the appropriate provider
            provider = agent_provider_manager.get_provider(agent.framework)
            if not provider:
                return {
                    "success": False,
                    "error": f"Framework {agent.framework} not supported",
                    "status_code": 404
                }
            
            # Delete the agent
            success = provider.delete_agent(agent_id)
            
            if success:
                logger.info(f"Deleted agent {agent_id}")
                return {
                    "success": True,
                    "status": "deleted",
                    "message": f"Agent {agent_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to delete agent",
                    "status_code": 500
                }
                
        except Exception as e:
            logger.error(f"Error deleting agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to delete agent: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def get_agent_versions(agent_id: int) -> Dict[str, Any]:
        """
        Get version history for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dict containing version history
        """
        try:
            # Check if agent exists
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }

            # Get all versions for this agent
            versions = db_repository.agents.get_agent_versions(agent_id)

            # Include current version
            current_version = {
                "id": None,
                "agent_id": agent.id,
                "version_number": agent.version,
                "name": agent.name,
                "description": agent.description,
                "framework": agent.framework,
                "model": agent.model,
                "created_at": agent.updated_at.isoformat() if agent.updated_at else None,
                "is_current": True
            }

            # Format response
            version_history = [current_version] + [
                {**v.to_dict(), "is_current": False}
                for v in versions
            ]

            return {
                "success": True,
                "versions": version_history
            }
            
        except Exception as e:
            logger.error(f"Error getting agent versions {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get agent versions: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def restore_agent_version(agent_id: int, version_number: int) -> Dict[str, Any]:
        """
        Restore an agent to a previous version.
        
        Args:
            agent_id: ID of the agent
            version_number: Version number to restore to
            
        Returns:
            Dict containing success status and restored agent details
        """
        try:
            # Check if agent exists
            agent = db_repository.agents.get_agent_by_id(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent with ID {agent_id} not found",
                    "status_code": 404
                }

            # Get the specified version
            version = db_repository.agents.get_agent_version(agent_id, version_number)
            if not version:
                return {
                    "success": False,
                    "error": f"Version {version_number} for agent {agent_id} not found",
                    "status_code": 404
                }

            # Restore agent using repository method
            success = db_repository.agents.restore_agent_from_version(agent_id, version)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to restore agent version",
                    "status_code": 500
                }

            # Get updated agent
            restored_agent = db_repository.agents.get_agent_by_id(agent_id)

            # Get the provider and update cache
            provider = agent_provider_manager.get_provider(restored_agent.framework)
            if provider and agent_id in provider.agents:
                provider.agents[agent_id]["config"] = restored_agent.to_dict()

            logger.info(f"Restored agent {agent_id} to version {version_number}")
            return {
                "success": True,
                "agent_id": agent_id,
                "message": f"Agent restored to version {version_number}",
                "agent": restored_agent.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error restoring agent version {agent_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to restore agent version: {str(e)}",
                "status_code": 500
            }
