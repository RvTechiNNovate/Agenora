"""
Pydantic schemas for the agent dashboard application.
"""
from pydantic import BaseModel as PydanticBaseModel, Field as PydanticField, create_model
from typing import List, Dict, Optional, Any, Union

# Export renamed imports as original names to maintain compatibility
BaseModel = PydanticBaseModel
Field = PydanticField

# LLM Provider schemas
class ProviderResponse(BaseModel):
    name: str
    display_name: str
    
class ModelResponse(BaseModel):
    id: str
    name: str
    provider: str
    context_window: Optional[int] = None
    max_tokens: Optional[int] = None
    price_per_1000_input_tokens: Optional[float] = None
    price_per_1000_output_tokens: Optional[float] = None

# Agent schemas
class ModelSettings(BaseModel):
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "temperature": 0.7,
                "max_tokens": 2048
            }
        }
    }

class BaseAgentTask(BaseModel):
    name: str = Field(..., description="Name of the agent")
    description: str = Field(..., description="Description of the agent's purpose")
    framework: str = Field(..., description="Agent framework to use (crewai, langchain, etc.)")
    model: str = Field("gpt-3.5-turbo", description="Language model to use")
    model_settings: Optional[ModelSettings] = Field(None, description="Model configuration settings")
    human_input_mode: Optional[str] = "NEVER"
    
class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    framework: str
    model: str
    model_config: dict = Field(default_factory=dict)
    status: str
    error: Optional[str] = None
    version: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Framework-specific fields will be included based on the agent type
    # These are added dynamically at runtime when converting from AgentModel
    
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }
        
class AgentCreateResponse(BaseModel):
    agent_id: int
    agent: AgentResponse

# Agent execution schemas
class QueryRequest(BaseModel):
    query: str = Field(..., description="The query text to send to the agent")
    conversation_id: Optional[str] = None
    config: Optional[dict] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "What are the latest trends in artificial intelligence?"
            }
        }
    }
    
class QueryResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    metadata: Optional[dict] = None

class StreamResponseItem(BaseModel):
    token: str
    conversation_id: Optional[str] = None
    finish_reason: Optional[str] = None
    is_finished: bool = False

# Settings schemas
class Settings(BaseModel):
    settings: Dict[str, Dict[str, Dict[str, str]]]


class FrameworkSchema(BaseModel):
    name: str
    description: str
    fields: Dict[str, str]

class FrameworkResponse(BaseModel):
    frameworks: Dict[str, FrameworkSchema]
    common_fields: Dict[str, str]


# Framework-specific config schemas
class CrewAIAgentConfig(BaseModel):
    role: str = "Assistant"
    backstory: str = "I'm an AI assistant created to help with various tasks."
    task: str = "Answer user queries as they come in."
    goals: Optional[List[str]] = None
    memory_enabled: Optional[bool] = None
    expected_output: Optional[str] = None

class LangChainAgentConfig(BaseModel):
    agent_type: str = "conversational"
    tools: List[str] = Field(default_factory=list)
    memory_type: Optional[str] = None
    verbose: Optional[bool] = False
    chain_type: Optional[str] = None

class AgnoAgentConfig(BaseModel):
    tools: List[str] = Field(default_factory=list)
    instructions: List[str] = Field(default_factory=lambda: ["Use tables to display data.", "Be concise and informative."])
    markdown: bool = True
    stream: bool = True

# Framework-specific task schemas
class CrewAIAgentTask(BaseAgentTask):
    """CrewAI specific agent configuration."""
    role: str = Field("Assistant", description="Role the agent should take")
    backstory: str = Field("I'm an AI assistant created to help with various tasks.", 
                          description="Background story for the agent")
    task: str = Field("Answer user queries as they come in.", 
                     description="Task description for the agent to perform")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Research Assistant",
                "description": "An AI assistant that helps with research tasks",
                "framework": "crewai",
                "role": "Senior Research Analyst",
                "backstory": "You are a knowledgeable research assistant with expertise in data analysis.",
                "task": "Provide in-depth research and analysis on various topics",
                "model": "gpt-3.5-turbo",
                "model_settings": {"temperature": 0.7}
            }
        }
    }

class LangChainAgentTask(BaseAgentTask):
    """LangChain specific agent configuration."""
    agent_type: str = Field("conversational", 
                           description="Type of LangChain agent to create")
    tools: List[str] = Field([], 
                            description="List of tool names to add to the agent")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Research Assistant",
                "description": "An AI assistant that helps with research tasks",
                "framework": "langchain",
                "agent_type": "conversational",
                "tools": [],
                "model": "gpt-3.5-turbo",
                "model_settings": {"temperature": 0.7}
            }
        }
    }

class AgnoAgentTask(BaseAgentTask):
    """Agno specific agent configuration."""
    tools: List[str] = Field([], 
                           description="List of tool names to add to the agent")
    instructions: List[str] = Field(["Use tables to display data.", "Be concise and informative."],
                                  description="List of instructions for the agent")
    markdown: bool = Field(True,
                         description="Enable markdown formatting in responses")
    stream: bool = Field(True,
                       description="Stream responses instead of waiting for completion")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Stock Analyst",
                "description": "An AI assistant that helps with stock market analysis",
                "framework": "agno",
                "tools": ["yfinance", "wikipedia"],
                "instructions": ["Use tables to display data.", "Be concise and informative."],
                "markdown": True,
                "stream": True,
                "model": "claude-3-7-sonnet-latest",
                "model_settings": {"temperature": 0.7}
            }
        }
    }
    tools: List[str] = Field(default_factory=list)
    instructions: List[str] = Field(default_factory=lambda: ["You are a helpful assistant."])
    markdown: bool = True
    stream: bool = True
