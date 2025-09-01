"""
Groq provider implementation.
"""
import os
from typing import Optional, List
from langchain_groq import ChatGroq
from backend.llm_manager.providers.config import llm_config as config
from backend.core.logging import get_logger
from backend.llm_manager.base import BaseLLMProvider

logger = get_logger(__name__)

class GroqProvider(BaseLLMProvider):
    """Groq LLM provider."""
    
    def __init__(self):
        # Check that API key is available
        self.api_key = config.groq_api_key
        if not self.api_key:
            logger.warning("Groq API key not found in environment variables or config")
            
        # List of supported models
        self._models = [
            "llama3-8b-8192",
            "llama3-70b-8192",
            "llama2-70b-4096",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        
    def get_llm(self, model: str = "llama3-8b-8192", temperature: float = 0.7, 
                max_tokens: Optional[int] = None, **kwargs) -> ChatGroq:
        """Get a Groq ChatGroq instance."""
        # Prepare parameters
        params = {
            "model_name": model,
            "temperature": temperature,
        }
        
        # Add optional parameters if provided
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        # Add any additional parameters
        params.update(kwargs)
        
        # Create and return the ChatGroq instance
        return ChatGroq(**params)
        
    @property
    def provider_name(self) -> str:
        """Return the name of this LLM provider."""
        return "groq"
        
    @property
    def available_models(self) -> List[str]:
        """Return a list of available models for this provider."""
        return self._models
        
    def validate_config(self) -> bool:
        """Validate that the necessary configuration is available."""
        return bool(self.api_key)
