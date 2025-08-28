"""
Base LLM provider module.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def get_llm(self, model: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> Any:
        """
        Get an LLM instance from this provider.
        
        Args:
            model: The model name/identifier
            temperature: The temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            An LLM instance compatible with LangChain/CrewAI
        """
        pass
        
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this LLM provider."""
        pass
        
    @property
    @abstractmethod
    def available_models(self) -> list:
        """Return a list of available models for this provider."""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate that the necessary configuration is available."""
        pass
