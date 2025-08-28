"""
Agent provider manager module.
"""
from typing import Dict, List, Any, Optional
from backend.utils.logging import get_logger
from backend.agent_manager.base import BaseAgentManager
from backend.agent_manager.factory import AgentManagerFactory

logger = get_logger(__name__)

class AgentProviderManager:
    """Manager for agent providers/frameworks."""
    
    def __init__(self, framework_list: Optional[List[str]] = None):
        """
        Initialize the manager with available agent frameworks.
        
        Args:
            framework_list: Optional list of framework names to initialize.
                          If None, all registered frameworks will be initialized.
        """
        self.providers = {}
        
        # Get list of frameworks to initialize
        if framework_list is None:
            framework_list = AgentManagerFactory.get_available_frameworks()
            
        # Initialize requested frameworks
        for framework in framework_list:
            provider = AgentManagerFactory.create_manager(framework)
            if provider:
                self.register_provider(framework, provider)
      
        # Set default framework
        self.default_framework = "crewai"
        if self.default_framework not in self.providers:
            if len(self.providers) > 0:
                self.default_framework = list(self.providers.keys())[0]
            else:
                logger.error("No valid agent providers available")
    
    def register_provider(self, framework: str, provider: BaseAgentManager) -> None:
        """Register a provider with this manager."""
        self.providers[framework] = provider
        logger.info(f"Registered {framework} agent provider")
            
    def get_provider(self, framework: str) -> Optional[BaseAgentManager]:
        """Get a provider by framework name."""
        return self.providers.get(framework)
            
    def get_default_provider(self) -> Optional[BaseAgentManager]:
        """Get the default provider."""
        return self.providers.get(self.default_framework)
        
    def list_providers(self) -> List[Dict[str, Any]]:
        """
        Return a list of available providers with details.
        
        Returns:
            List of dicts with provider details including framework and features
        """
        providers_list = []
        for framework, provider in self.providers.items():
            providers_list.append({
                "framework": framework,
                "name": framework.capitalize(),
                "features": getattr(provider, "supported_features", []),
                "status": "active"
            })
        
        return providers_list
        
    def get_provider_features(self, framework: str = None) -> Dict[str, List[str]]:
        """
        Get supported features for specified framework or all frameworks.
        
        Args:
            framework: Optional framework name to get features for
            
        Returns:
            Dict mapping framework names to their supported features
        """
        if framework and framework in self.providers:
            provider = self.providers[framework]
            return {
                framework: getattr(provider, "supported_features", [])
            }
            
        # Return features for all frameworks
        features = {}
        for framework, provider in self.providers.items():
            features[framework] = getattr(provider, "supported_features", [])
                
        return features

# Create a singleton instance
agent_provider_manager = AgentProviderManager()
