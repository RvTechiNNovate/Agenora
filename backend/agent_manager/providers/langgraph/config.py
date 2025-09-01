"""
Langgraph agent configuration module.
"""
from typing import List, Dict, Any, Optional

class LanggraphConfig:
    """Configuration for Langgraph agents."""
    
    def __init__(
        self, 
        prompt:str,
        tools: Optional[List[str]] = None,
    ):
        """Initialize Langgraph configuration."""
        self.prompt = prompt
        self.tools = tools or []
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "LanggraphConfig":
        """Create config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            LanggraphConfig object
        """
        return cls(
            prompt=config_dict.get("prompt"),
            tools=config_dict.get("tools", []),
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "prompt": self.prompt,
            "tools": self.tools,
        }
        

