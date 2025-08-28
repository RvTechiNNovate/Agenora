from fastapi import APIRouter, Depends
from typing import Optional

from backend.config import config
from backend.utils.security import verify_api_key
from backend.agent_manager import managers

# Create router
router = APIRouter(prefix="/api", tags=["frameworks"])

@router.get("/frameworks/schema",
        summary="Get available frameworks and their schemas",
        description="Returns the list of supported agent frameworks and their input schemas.")
async def get_framework_schemas():
    """Get all available frameworks and their schemas."""
    # Define the fields for each framework
    frameworks = {
        "crewai": {
            "name": "CrewAI",
            "description": "Multi-agent framework for creating agent teams",
            "fields": {
                "role": {
                    "type": "string",
                    "description": "Role the agent should take",
                    "default": "Assistant",
                    "required": True
                },
                "backstory": {
                    "type": "string",
                    "description": "Background story for the agent",
                    "default": "I'm an AI assistant created to help with various tasks.",
                    "required": True
                },
                "task": {
                    "type": "string",
                    "description": "Task description for the agent to perform",
                    "default": "Answer user queries as they come in.",
                    "required": True
                }
            }
        },
        "langchain": {
            "name": "LangChain",
            "description": "Framework for building applications with LLMs",
            "fields": {
                "agent_type": {
                    "type": "string",
                    "description": "Type of LangChain agent to create",
                    "default": "conversational",
                    "enum": ["conversational", "zero-shot-react-description", "react-docstore", "structured-chat"],
                    "required": True
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tool names to add to the agent",
                    "default": [],
                    "required": False
                }
            }
        }
    }
    
    # Define the common fields for all frameworks
    common_fields = {
        "name": {
            "type": "string",
            "description": "Name of the agent",
            "required": True
        },
        "description": {
            "type": "string",
            "description": "Description of the agent's purpose",
            "required": True
        },
        "framework": {
            "type": "string",
            "description": "Agent framework to use",
            "enum": list(frameworks.keys()),
            "required": True
        },
        "model": {
            "type": "string",
            "description": "Language model to use",
            "default": "gpt-3.5-turbo",
            "required": True
        },
        "model_settings": {
            "type": "object",
            "description": "Model configuration settings",
            "properties": {
                "temperature": {"type": "number", "minimum": 0, "maximum": 1},
                "max_tokens": {"type": "integer"},
                "top_p": {"type": "number"}
            },
            "required": False
        }
    }
    
    return {
        "frameworks": frameworks,
        "common_fields": common_fields
    }

@router.get("/frameworks",
        summary="Get available frameworks",
        description="Returns the list of supported agent frameworks.")
async def get_frameworks():
    """Get all available frameworks."""
    return {
        "frameworks": list(managers.keys())
    }

@router.get("/llm/providers",
        summary="List available LLM providers",
        description="Get a list of all supported LLM providers.")
async def list_llm_providers():
    """List all supported LLM providers."""
    from backend.llm_providers.manager import llm_provider_manager
    return {"providers": llm_provider_manager.list_providers()}

@router.get("/llm/models",
        summary="List available LLM models",
        description="Get a list of available models, optionally filtered by provider.")
async def list_llm_models(provider: Optional[str] = None):
    """List available models for a provider or all providers."""
    from backend.llm_providers.manager import llm_provider_manager
    return {"models": llm_provider_manager.list_models(provider)}
