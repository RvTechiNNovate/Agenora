"""
Database repository module for centralized database operations.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from backend.db.session import SessionLocal
from backend.db.models import AgentModel, AgentVersionModel
from backend.core.logging import get_logger

logger = get_logger(__name__)


class AgentRepository:
    """Repository class for Agent database operations."""
    
    @staticmethod
    def create_agent(agent_data: Dict[str, Any]) -> int:
        """Create a new agent in the database."""
        try:
            db = SessionLocal()
            
            # Create base agent model
            db_agent = AgentModel(
                name=agent_data["name"],
                description=agent_data.get("description"),
                framework=agent_data["framework"],
                model=agent_data.get("model"),
                model_config=agent_data.get("model_config"),
                status="stopped"
            )
            db.add(db_agent)
            db.commit()
            db.refresh(db_agent)
            
            logger.info(f"Created agent {db_agent.id}: {agent_data.get('name')}")
            return db_agent.id
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def create_agent_with_framework_config(agent_data: Dict[str, Any], 
                                          framework_config_callback: callable = None) -> int:
        """Create a new agent with framework-specific configuration."""
        try:
            db = SessionLocal()
            
            # Create base agent model
            db_agent = AgentModel(
                name=agent_data["name"],
                description=agent_data.get("description"),
                framework=agent_data["framework"],
                model=agent_data.get("model"),
                model_config=agent_data.get("model_config"),
                status="stopped"
            )
            db.add(db_agent)
            db.flush()  # Get the ID without committing
            
            # Allow framework-specific configuration
            if framework_config_callback:
                framework_config_callback(db, db_agent, agent_data)
            
            db.commit()
            db.refresh(db_agent)
            
            logger.info(f"Created agent {db_agent.id}: {agent_data.get('name')}")
            return db_agent.id
            
        except Exception as e:
            logger.error(f"Error creating agent with framework config: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def update_agent_with_framework_config(agent_id: int, 
                                         agent_data: Dict[str, Any],
                                         framework_config_callback: callable = None) -> bool:
        """Update an existing agent with framework-specific configuration."""
        try:
            db = SessionLocal()
            db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            
            if not db_agent:
                logger.warning(f"Agent {agent_id} not found for update")
                return False
                
            # Update base fields
            if "name" in agent_data:
                db_agent.name = agent_data["name"]
            if "description" in agent_data:
                db_agent.description = agent_data["description"]
            if "model" in agent_data:
                db_agent.model = agent_data["model"]
            if "model_config" in agent_data:
                db_agent.model_config = agent_data["model_config"]
            if "status" in agent_data:
                db_agent.status = agent_data["status"]
            if "error" in agent_data:
                db_agent.error = agent_data["error"]
            
            # Allow framework-specific configuration updates
            if framework_config_callback:
                framework_config_callback(db, db_agent, agent_data)
            
            db.commit()
            logger.info(f"Updated agent {agent_id} with framework config")
            return True
            
        except Exception as e:
            logger.error(f"Error updating agent {agent_id} with framework config: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def get_agent_by_id(agent_id: int) -> Optional[AgentModel]:
        """Get an agent by ID."""
        try:
            db = SessionLocal()
            agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            return agent
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {str(e)}")
            return None
        finally:
            db.close()

    @staticmethod
    def update_agent(agent_id: int, agent_data: Dict[str, Any]) -> bool:
        """Update an existing agent."""
        try:
            db = SessionLocal()
            db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            
            if not db_agent:
                logger.warning(f"Agent {agent_id} not found for update")
                return False
                
            # Update base fields
            if "name" in agent_data:
                db_agent.name = agent_data["name"]
            if "description" in agent_data:
                db_agent.description = agent_data["description"]
            if "model" in agent_data:
                db_agent.model = agent_data["model"]
            if "model_config" in agent_data:
                db_agent.model_config = agent_data["model_config"]
            if "status" in agent_data:
                db_agent.status = agent_data["status"]
            if "error" in agent_data:
                db_agent.error = agent_data["error"]
            
            db.commit()
            logger.info(f"Updated agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def delete_agent(agent_id: int) -> bool:
        """Delete an agent from the database."""
        try:
            db = SessionLocal()
            db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            
            if not db_agent:
                logger.warning(f"Agent {agent_id} not found for deletion")
                return False
                
            db.delete(db_agent)
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting agent {agent_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def get_all_agents(framework: Optional[str] = None) -> List[AgentModel]:
        """Get all agents, optionally filtered by framework."""
        try:
            db = SessionLocal()
            query = db.query(AgentModel)
            
            if framework:
                query = query.filter(AgentModel.framework == framework)
                
            agents = query.all()
            return agents
            
        except Exception as e:
            logger.error(f"Error getting all agents: {str(e)}")
            return []
        finally:
            db.close()

    @staticmethod
    def update_agent_status(agent_id: int, status: str, error: Optional[str] = None) -> bool:
        """Update agent status and error message."""
        try:
            db = SessionLocal()
            db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            
            if not db_agent:
                logger.warning(f"Agent {agent_id} not found for status update")
                return False
                
            db_agent.status = status
            if error is not None:
                db_agent.error = error
                
            db.commit()
            logger.info(f"Updated agent {agent_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating agent status: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def get_agents_by_framework(framework: str) -> List[AgentModel]:
        """Get all agents for a specific framework."""
        # Return agents with the session still active - each manager will be responsible
        # for extracting what it needs while the session is open
        db = SessionLocal()
        try:
            # Get agents without loading any lazy-loaded attributes
            # The specific framework manager will handle loading what it needs
            agents = db.query(AgentModel).filter(AgentModel.framework == framework).all()
            return agents
            
        except Exception as e:
            logger.error(f"Error getting agents for framework {framework}: {str(e)}")
            return []
        finally:
            db.close()

    @staticmethod
    def create_agent_version(agent: AgentModel, version_number: int) -> bool:
        """Create a version snapshot of an agent."""
        try:
            db = SessionLocal()
            version = AgentVersionModel.from_dict(agent, version_number)
            db.add(version)
            db.commit()
            
            logger.info(f"Created version {version_number} for agent {agent.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating agent version: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def get_agent_versions(agent_id: int) -> List[AgentVersionModel]:
        """Get all versions for an agent."""
        try:
            db = SessionLocal()
            versions = db.query(AgentVersionModel).filter(
                AgentVersionModel.agent_id == agent_id
            ).order_by(AgentVersionModel.version_number.desc()).all()
            return versions
            
        except Exception as e:
            logger.error(f"Error getting agent versions for agent {agent_id}: {str(e)}")
            return []
        finally:
            db.close()

    @staticmethod
    def get_agent_version(agent_id: int, version_number: int) -> Optional[AgentVersionModel]:
        """Get a specific version of an agent."""
        try:
            db = SessionLocal()
            version = db.query(AgentVersionModel).filter(
                AgentVersionModel.agent_id == agent_id,
                AgentVersionModel.version_number == version_number
            ).first()
            return version
            
        except Exception as e:
            logger.error(f"Error getting agent version {version_number} for agent {agent_id}: {str(e)}")
            return None
        finally:
            db.close()

    @staticmethod
    def restore_agent_from_version(agent_id: int, version: AgentVersionModel) -> bool:
        """Restore an agent from a version snapshot."""
        try:
            db = SessionLocal()
            
            # Get the current agent
            agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
            if not agent:
                return False
            
            # Create version of current state before restoring
            current_version = AgentVersionModel.from_dict(agent, agent.version)
            db.add(current_version)
            
            # Restore agent base fields
            agent.name = version.name
            agent.description = version.description
            agent.framework = version.framework
            agent.model = version.model
            agent.model_config = version.model_config
            agent.version = agent.version + 1
            
            # Restore framework-specific configuration if available
            if version.framework_config:
                # Handle CrewAI specific fields
                if version.framework == "crewai" and agent.crewai_config:
                    agent.crewai_config.role = version.framework_config.get("role", "Assistant")
                    agent.crewai_config.backstory = version.framework_config.get("backstory", "")
                    agent.crewai_config.task = version.framework_config.get("task", "")
                    agent.crewai_config.goals = version.framework_config.get("goals", [])
                    agent.crewai_config.tools = version.framework_config.get("tools", [])
                    agent.crewai_config.memory_enabled = version.framework_config.get("memory_enabled", False)
                    agent.crewai_config.expected_output = version.framework_config.get("expected_output", "")
                
                # Handle LangChain specific fields
                elif version.framework == "langchain" and agent.langchain_config:
                    agent.langchain_config.agent_type = version.framework_config.get("agent_type", "zero-shot-react-description")
                    agent.langchain_config.tools = version.framework_config.get("tools", [])
                    agent.langchain_config.memory_type = version.framework_config.get("memory_type", "buffer")
                    agent.langchain_config.verbose = version.framework_config.get("verbose", False)
                    agent.langchain_config.chain_type = version.framework_config.get("chain_type", "stuff")
                
                # Handle Agno specific fields
                elif version.framework == "agno" and agent.agno_config:
                    agent.agno_config.tools = version.framework_config.get("tools", [])
                    agent.agno_config.instructions = version.framework_config.get("instructions", "")
                    agent.agno_config.markdown = version.framework_config.get("markdown", False)
                    agent.agno_config.stream = version.framework_config.get("stream", True)
                
                # Handle Langgraph specific fields
                elif version.framework == "langgraph" and agent.langgraph_config:
                    agent.langgraph_config.tools = version.framework_config.get("tools", [])
                    agent.langgraph_config.prompt = version.framework_config.get("prompt", "")
            
            db.commit()
            
            logger.info(f"Restored agent {agent_id} from version {version.version_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring agent {agent_id} from version: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()


class SettingRepository:
    """Repository class for Settings database operations."""
    
    @staticmethod
    def create_setting(setting_data: Dict[str, Any]) -> int:
        """Create a new setting in the database."""
        # TODO: Implement when SettingModel is available
        pass

    @staticmethod
    def get_setting_by_id(setting_id: int) -> Optional[Any]:
        """Get a setting by ID."""
        # TODO: Implement when SettingModel is available
        pass

    @staticmethod
    def update_setting(setting_id: int, setting_data: Dict[str, Any]) -> bool:
        """Update an existing setting."""
        # TODO: Implement when SettingModel is available
        pass

    @staticmethod
    def delete_setting(setting_id: int) -> bool:
        """Delete a setting from the database."""
        # TODO: Implement when SettingModel is available
        pass

    @staticmethod
    def get_all_settings() -> List[Any]:
        """Get all settings."""
        # TODO: Implement when SettingModel is available
        pass


class UserRepository:
    """Repository class for User database operations."""
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> int:
        """Create a new user in the database."""
        # TODO: Implement when UserModel is available
        pass

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Any]:
        """Get a user by ID."""
        # TODO: Implement when UserModel is available
        pass

    @staticmethod
    def update_user(user_id: int, user_data: Dict[str, Any]) -> bool:
        """Update an existing user."""
        # TODO: Implement when UserModel is available
        pass

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete a user from the database."""
        # TODO: Implement when UserModel is available
        pass

    @staticmethod
    def get_all_users() -> List[Any]:
        """Get all users."""
        # TODO: Implement when UserModel is available
        pass


class CommonRepository:
    """Main repository class that provides access to all repositories."""
    
    def __init__(self):
        self.agents = AgentRepository()
        self.settings = SettingRepository()
        self.users = UserRepository()


# Create a singleton instance
db_repository = CommonRepository()