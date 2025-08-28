"""
LLM provider factory module.
"""
from typing import Dict, Type, Optional, List
from backend.utils.logging import get_logger
from backend.llm_providers.base import BaseLLMProvider
from backend.llm_providers.providers.openai.provider import OpenAIProvider
from backend.llm_providers.providers.azure.provider import AzureOpenAIProvider
from backend.llm_providers.providers.groq.provider import GroqProvider

logger = get_logger(__name__)

class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    _registered_providers: Dict[str, Type[BaseLLMProvider]] = {
        "openai": OpenAIProvider,
        "azure": AzureOpenAIProvider,
        "groq": GroqProvider,
    }
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """
        Register a new provider type.
        
        Args:
            provider_name: The name/identifier for the provider
            provider_class: The provider class to register
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError(f"Provider class must inherit from BaseLLMProvider")
        cls._registered_providers[provider_name] = provider_class
        logger.info(f"Registered new provider type: {provider_name}")
        
    @classmethod
    def create_provider(cls, provider_name: str, **kwargs) -> Optional[BaseLLMProvider]:
        """
        Create a provider instance by name.
        
        Args:
            provider_name: The name of the provider to create
            **kwargs: Additional configuration parameters for the provider
            
        Returns:
            An instance of the requested provider or None if creation fails
        """
        provider_class = cls._registered_providers.get(provider_name)
        if not provider_class:
            logger.error(f"Unknown provider type: {provider_name}")
            return None
            
        try:
            provider = provider_class(**kwargs)
            if provider.validate_config():
                return provider
            else:
                logger.error(f"Provider {provider_name} failed validation")
                return None
        except Exception as e:
            logger.error(f"Failed to create provider {provider_name}: {str(e)}")
            return None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of registered provider types."""
        return list(cls._registered_providers.keys())
