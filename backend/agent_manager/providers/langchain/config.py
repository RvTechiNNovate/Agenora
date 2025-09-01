"""
LangChain agent configuration module.
"""
from typing import List, Dict, Any, Optional

class LangChainConfig:
    """Configuration for LangChain agents."""
    
    def __init__(
        self, 
        agent_type: str = "conversational", 
        tools: Optional[List[str]] = None,
        memory_type: Optional[str] = None, 
        verbose: bool = False,
        chain_type: Optional[str] = None
    ):
        """Initialize LangChain configuration.
        
        Args:
            agent_type: The type of agent to create (e.g., "conversational", "zero-shot-react-description")
            tools: List of tools for the agent to use
            memory_type: The type of memory to use (e.g., "buffer", "conversation_buffer")
            verbose: Whether to enable verbose output
            chain_type: The type of chain to use (e.g., "stuff", "map_reduce")
        """
        self.agent_type = agent_type
        self.tools = tools or []
        self.memory_type = memory_type
        self.verbose = verbose
        self.chain_type = chain_type
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "LangChainConfig":
        """Create config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            LangChainConfig object
        """
        return cls(
            agent_type=config_dict.get("agent_type", "conversational"),
            tools=config_dict.get("tools", []),
            memory_type=config_dict.get("memory_type"),
            verbose=config_dict.get("verbose", False),
            chain_type=config_dict.get("chain_type")
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "agent_type": self.agent_type,
            "tools": self.tools,
            "memory_type": self.memory_type,
            "verbose": self.verbose,
            "chain_type": self.chain_type
        }
