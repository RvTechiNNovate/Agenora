"""
LLM provider manager module.
"""
from typing import Dict, List, Any, Optional
from backend.utils.logging import get_logger
from backend.llm_providers.base import BaseLLMProvider
from backend.llm_providers.factory import LLMProviderFactory

logger = get_logger(__name__)

class LLMProviderManager:
    """Manager for LLM providers."""
    
    def __init__(self):
        """
        Initialize the manager with available providers.
        
        Args:
            provider_names: Optional list of provider names to initialize.
                          If None, all registered providers will be initialized.
        """
        self.providers = {}
        
        # Get list of providers to initialize
        
        provider_names = LLMProviderFactory.get_available_providers()
            
        # Initialize requested providers
        for provider_name in provider_names:
            provider = LLMProviderFactory.create_provider(provider_name)
            if provider:
                self.register_provider(provider)
      
        # Set default provider
        self.default_provider_name = "openai"
        if self.default_provider_name not in self.providers:
            if len(self.providers) > 0:
                self.default_provider_name = list(self.providers.keys())[0]
            else:
                logger.error("No valid LLM providers available")
    
    def register_provider(self, provider: BaseLLMProvider) -> None:
        """Register a provider with this manager."""
        name = provider.provider_name
        if provider.validate_config():
            self.providers[name] = provider
            logger.info(f"Registered {name} LLM provider with {len(provider.available_models)} models")
        else:
            logger.warning(f"LLM provider {name} failed validation, not registering")
            
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Get a provider by name."""
        return self.providers.get(name)
            
    def get_default_provider(self) -> Optional[BaseLLMProvider]:
        """Get the default provider."""
        return self.providers.get(self.default_provider_name)
        
    def get_llm(self, provider_name: str = None, model: str = None, 
               temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> Any:
        """
        Get an LLM from a specific provider.
        
        Args:
            provider_name: The name of the provider, or None to use default
            model: The model name/identifier
            temperature: The temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            An LLM instance compatible with LangChain/CrewAI or None if provider not available
        """
        # Parse model string if it includes provider info (e.g., "openai:gpt-4")
        if model and ":" in model and not provider_name:
            parts = model.split(":", 1)
            provider_name, model = parts
        
        # Get the requested provider or default
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
        else:
            provider = self.get_default_provider()
            
        if not provider:
            logger.error("No valid LLM provider available")
            return None
            
        # Use provider to create LLM
        return provider.get_llm(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)
        
    def list_providers(self) -> List[Dict[str, str]]:
        """
        Return a list of available providers with details.
        
        Returns:
            List of dicts with provider details including id and name
        """
        providers_list = []
        for provider_id, provider in self.providers.items():
            # Format provider name for display (e.g., "openai" -> "OpenAI")
            display_name = provider_id.capitalize()
            
            # Special case handling
            if provider_id == "openai":
                display_name = "OpenAI"
            elif provider_id == "azure":
                display_name = "Azure OpenAI"
            elif provider_id == "groq":
                display_name = "Groq"
            
            providers_list.append({
                "id": provider_id,
                "name": display_name,
                "model_count": len(provider.available_models)
            })
        
        return providers_list
        
    def list_models(self, provider_name: str = None) -> List[str]:
        """
        Return a list of available models.
        
        If provider_name is specified, return only models from that provider.
        Otherwise, return all models from all providers with provider prefix.
        """
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name].available_models
            
        # Return all models from all providers with provider prefix
        models = []
        for name, provider in self.providers.items():
            for model in provider.available_models:
                models.append(f"{name}:{model}")
                
        return models

# Create a singleton instance with all available providers
llm_provider_manager = LLMProviderManager()
