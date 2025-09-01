"""
Pydantic schemas for the agent dashboard application.
"""
from pydantic import BaseModel as PydanticBaseModel, Field as PydanticField, create_model
from typing import List, Dict, Optional, Any, Union

# Export renamed imports as original names to maintain compatibility
BaseModel = PydanticBaseModel
Field = PydanticField

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
    name: str 
    description: str 
    framework: str 
    model: str 
    model_settings: Optional[ModelSettings] = None
    human_input_mode: Optional[str] = "NEVER"
    
class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    framework: str
    model: str
    model_config: dict 
    status: str
    error: Optional[str] = None
    version: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
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

