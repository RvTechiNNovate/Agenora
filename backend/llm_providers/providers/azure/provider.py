"""
Azure OpenAI provider implementation.
"""
import os
from typing import Dict, Any, Optional, List
from langchain_openai import AzureChatOpenAI
from backend.llm_providers.providers.config import llm_config as config
from backend.utils.logging import get_logger
from backend.llm_providers.base import BaseLLMProvider

logger = get_logger(__name__)

class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI LLM provider."""
    
    def __init__(self):
        # Check that required configuration is available
        self.api_key = config.azure_api_key
        self.endpoint = config.azure_endpoint
        self.api_version = config.azure_api_version 
        
        if not (self.api_key and self.endpoint and self.api_version):
            logger.warning("Azure OpenAI API key or endpoint or azure api version  not found")
            
        # Default deployment names for models
        self._model_deployments = {
            "gpt-3.5-turbo": "gpt-35-turbo",
            "gpt-4": "gpt-4",
            "gpt-4-turbo": "gpt-4-turbo"
        }
        
        # Override with configuration if available
        if hasattr(config.azure_deployments, "azure_deployments") and config.azure_deployments:
            self._model_deployments.update(config.azure_deployments)
        
    def get_llm(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7, 
                max_tokens: Optional[int] = None, **kwargs) -> AzureChatOpenAI:
        """Get an Azure OpenAI instance."""
        # Get deployment name for this model
        deployment_name = self._model_deployments.get(model, model)
        
        # Prepare parameters
        params = {
            "deployment_name": deployment_name,
            "api_key": self.api_key,
            "azure_endpoint": self.endpoint,
            "api_version": self.api_version,
            "temperature": temperature,
        }
        
        # Add optional parameters if provided
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        # Add any additional parameters
        params.update(kwargs)
        
        # Create and return the AzureChatOpenAI instance
        return AzureChatOpenAI(**params)
        
    @property
    def provider_name(self) -> str:
        """Return the name of this LLM provider."""
        return "azure"
        
    @property
    def available_models(self) -> List[str]:
        """Return a list of available models for this provider."""
        return list(self._model_deployments.keys())
        
    def validate_config(self) -> bool:
        """Validate that the necessary configuration is available."""
        return bool(self.api_key and self.endpoint)
