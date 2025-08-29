"""
CrewAI agent configuration module.
"""
from typing import List, Dict, Any, Optional

class CrewAIConfig:
    """Configuration for CrewAI agents."""
    
    def __init__(
        self, 
        role: str, 
        backstory: str,
        task: str , 
        goals: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        memory_enabled: bool = False,
        expected_output: str = "A helpful response to the user's query"
    ):
        """Initialize CrewAI configuration.
        
        Args:
            role: The role the agent should take
            backstory: The background story for the agent
            task: The description of the task the agent should perform
            goals: List of goals for the agent to achieve
            tools: List of tools for the agent to use
            memory_enabled: Whether the agent should have memory enabled
            expected_output: Description of the expected output
        """
        self.role = role
        self.backstory = backstory
        self.task = task
        self.goals = goals or []
        self.tools = tools or []
        self.memory_enabled = memory_enabled
        self.expected_output = expected_output
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "CrewAIConfig":
        """Create config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            CrewAIConfig object
        """
        return cls(
            role=config_dict.get("role"),
            backstory=config_dict.get("backstory", "I'm an AI assistant created to help with various tasks."),
            task=config_dict.get("task", "Answer user queries as they come in."),
            goals=config_dict.get("goals", []),
            tools=config_dict.get("tools", []),
            memory_enabled=config_dict.get("memory_enabled", True),
            expected_output=config_dict.get("expected_output", "A helpful response to the user's query")
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "role": self.role,
            "backstory": self.backstory,
            "task": self.task,
            "goals": self.goals,
            "tools": self.tools,
            "memory_enabled": self.memory_enabled,
            "expected_output": self.expected_output
        }

