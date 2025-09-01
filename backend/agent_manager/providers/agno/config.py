"""
Agno agent configuration module.
"""
from typing import List, Dict, Any, Optional

class AgnoConfig:
    """Configuration for Agno agents."""
    
    def __init__(
        self, 
        model_id: str = "claude-3-7-sonnet-latest", 
        tools: Optional[List[str]] = None,
        instructions: Optional[List[str]] = None, 
        markdown: bool = True, 
        stream: bool = True
    ):
        """Initialize Agno configuration.
        
        Args:
            model_id: The ID of the model to use (e.g., "claude-3-7-sonnet-latest")
            tools: List of tools to provide to the agent
            instructions: List of instruction strings for the agent
            markdown: Whether to enable markdown formatting in responses
            stream: Whether to stream responses instead of waiting for completion
        """
        self.model_id = model_id
        self.tools = tools or []
        self.instructions = instructions or []
        self.markdown = markdown
        self.stream = stream
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AgnoConfig":
        """Create config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            AgnoConfig object
        """
        return cls(
            model_id=config_dict.get("model_id", "claude-3-7-sonnet-latest"),
            tools=config_dict.get("tools", []),
            instructions=config_dict.get("instructions", []),
            markdown=config_dict.get("markdown", True),
            stream=config_dict.get("stream", True)
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "model_id": self.model_id,
            "tools": self.tools,
            "instructions": self.instructions,
            "markdown": self.markdown,
            "stream": self.stream
        }
