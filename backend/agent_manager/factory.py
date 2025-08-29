"""
Agent manager factory module.
"""
from typing import Dict, Type, Optional, List
from backend.utils.logging import get_logger
from backend.agent_manager.base import BaseAgentManager
from backend.agent_manager.agent_providers.crewai.crewai_agent import CrewAIManager
from backend.agent_manager.agent_providers.langchain.langchain_agent import LangChainManager
from backend.agent_manager.agent_providers.agno.agno_agent import AgnoManager
logger = get_logger(__name__)

class AgentManagerFactory:
    """Factory for creating agent managers."""
    
    _registered_managers: Dict[str, Type[BaseAgentManager]] = {
        "crewai": CrewAIManager,
        "langchain": LangChainManager,
        "agno": AgnoManager
    }
    
    @classmethod
    def register_manager(cls, framework_name: str, manager_class: Type[BaseAgentManager]) -> None:
        """
        Register a new agent manager type.
        
        Args:
            framework_name: The name/identifier for the framework
            manager_class: The manager class to register
        """
        if not issubclass(manager_class, BaseAgentManager):
            raise ValueError(f"Manager class must inherit from BaseAgentManager")
        cls._registered_managers[framework_name] = manager_class
        logger.info(f"Registered new agent manager: {framework_name}")
        
    @classmethod
    def create_manager(cls, framework_name: str, **kwargs) -> Optional[BaseAgentManager]:
        """
        Create a manager instance by framework name.
        
        Args:
            framework_name: The name of the framework to create manager for
            **kwargs: Additional configuration parameters for the manager
            
        Returns:
            An instance of the requested manager or None if creation fails
        """
        manager_class = cls._registered_managers.get(framework_name)
        if not manager_class:
            logger.error(f"Unknown framework type: {framework_name}")
            return None
            
        try:
            manager = manager_class(**kwargs)
            return manager
        except Exception as e:
            logger.error(f"Failed to create manager for {framework_name}: {str(e)}")
            return None
    
    @classmethod
    def get_available_frameworks(cls) -> List[str]:
        """Get list of registered framework types."""
        return list(cls._registered_managers.keys())
