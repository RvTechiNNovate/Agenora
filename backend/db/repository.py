"""
Database repository module for centralized database operations.
"""
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from backend.db.session import SessionLocal
from backend.db.models import AgentModel
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
            logger.info(f"Deleted agent {agent_id}")
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
        try:
            db = SessionLocal()
            agents = db.query(AgentModel).filter(AgentModel.framework == framework).all()
            return agents
            
        except Exception as e:
            logger.error(f"Error getting agents for framework {framework}: {str(e)}")
            return []
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