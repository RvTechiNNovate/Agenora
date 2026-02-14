"""
Framework service module for business logic related to framework operations.
"""
from typing import Dict, List, Optional, Any
from backend.core.logging import get_logger
from backend.agent_manager import managers
from backend.llm_manager.manager import llm_provider_manager
from backend.schemas.schemas import FrameworkResponse

logger = get_logger(__name__)


class FrameworkService:
    """Service class for framework-related business operations."""
    
    @staticmethod
    def get_framework_schemas() -> FrameworkResponse:
        """
        Get all available frameworks and their schemas.
        
        Returns:
            FrameworkResponse containing frameworks and common fields
        """
        try:
            # Fetch framework schemas from agent managers
            frameworks = {}
            
            # Common fields for all frameworks
            common_fields = {
                "name": str,
                "description": str,
                "framework": str,
                "model": str,
                "model_config": dict
            }
            
            # Get schema from each manager dynamically
            for framework_name, manager in managers.items():
                if hasattr(manager, 'get_schema'):
                    # Use the manager's get_schema method if available
                    schema = manager.get_schema()
                    frameworks[framework_name] = schema
                else:
                    logger.error(f"Manager for {framework_name} does not implement get_schema()")
                    raise ValueError(f"Manager for {framework_name} does not implement get_schema()")

            return FrameworkResponse(
                frameworks=frameworks,
                common_fields=common_fields
            )
        except Exception as e:
            logger.error(f"Error getting framework schemas: {str(e)}")
            raise
    
    @staticmethod
    def get_frameworks() -> Dict[str, List[str]]:
        """
        Get all available frameworks.
        
        Returns:
            Dict containing list of framework names
        """
        try:
            return {
                "frameworks": list(managers.keys())
            }
        except Exception as e:
            logger.error(f"Error getting frameworks: {str(e)}")
            raise
    
    @staticmethod
    def list_llm_providers() -> Dict[str, List[str]]:
        """
        List all supported LLM providers.
        
        Returns:
            Dict containing list of provider names
        """
        try:
            return {"providers": llm_provider_manager.list_providers()}
        except Exception as e:
            logger.error(f"Error listing LLM providers: {str(e)}")
            raise
    
    @staticmethod
    def list_llm_models(provider: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List available models for a provider or all providers.
        
        Args:
            provider: Optional provider name to filter by
            
        Returns:
            Dict containing list of models
        """
        try:
            return {"models": llm_provider_manager.list_models(provider)}
        except Exception as e:
            logger.error(f"Error listing LLM models: {str(e)}")
            raise
