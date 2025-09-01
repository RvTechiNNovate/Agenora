"""Autogen agent configguration module"""

from typing import List, Dict, Any, Optional

class AutoGenConfig:
    """Configuration for AutoGen agents."""
    
    def __init__(
        self, 
        system_message: str,
       
        tools: Optional[List[str]] = None,
    ):
        """Initialize AutoGen configuration."""
        self.system_message = system_message
      
        self.tools = tools or []
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AutoGenConfig":
        """Create config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            AutoGenConfig object
        """
        return cls(
            system_message=config_dict.get("system_message"),
            tools=config_dict.get("tools", []),
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "system_message": self.system_message,
            "tools": self.tools,
        }
    