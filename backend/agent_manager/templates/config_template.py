"""
Configuration template for new agent framework.

This file defines the configuration structure for your agent framework.
Implement the necessary configuration classes and methods here.
"""
from typing import List, Dict, Any, Optional

class NewFrameworkConfig:
    """Configuration for NewFramework agents."""
    
    def __init__(
        self, 
        field1: str,
        field2: Optional[List[str]] = None,
        field3: bool = True,
        # Add any other fields your framework requires
    ):
        """
        Initialize NewFramework configuration.
        
        Args:
            field1: Primary configuration field (required)
            field2: List of string values (optional)
            field3: Boolean flag (default: True)
        """
        self.field1 = field1
        self.field2 = field2 or []
        self.field3 = field3
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "NewFrameworkConfig":
        """
        Create config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            NewFrameworkConfig object
        """
        return cls(
            field1=config_dict.get("field1", ""),
            field2=config_dict.get("field2", []),
            field3=config_dict.get("field3", True),
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "field1": self.field1,
            "field2": self.field2,
            "field3": self.field3,
        }

