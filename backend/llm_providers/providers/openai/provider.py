"""
OpenAI provider implementation.
"""
import os
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from backend.llm_providers.providers.config import llm_config as config
from backend.utils.logging import get_logger
from backend.llm_providers.base import BaseLLMProvider

logger = get_logger(__name__)

class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self):
        # Check that API key is available
        self.api_key = config.openai_api_key
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables or config")
            
        # List of supported models
        self._models = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4-turbo"
        ]
        
    def get_llm(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7, 
                max_tokens: Optional[int] = None, **kwargs) -> ChatOpenAI:
        """Get an OpenAI ChatOpenAI instance."""
        # Prepare parameters
        params = {
            "model": model,
            "temperature": temperature,
        }
        
        # Add optional parameters if provided
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        # Add any additional parameters
        params.update(kwargs)
        
        # Create and return the ChatOpenAI instance
        return ChatOpenAI(**params)
        
    @property
    def provider_name(self) -> str:
        """Return the name of this LLM provider."""
        return "openai"
        
    @property
    def available_models(self) -> List[str]:
        """Return a list of available models for this provider."""
        return self._models
        
    def validate_config(self) -> bool:
        """Validate that the necessary configuration is available."""
        return bool(self.api_key)
