import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv
# Load environment variables from .env file if present
load_dotenv()

class LLMConfig(BaseModel):
    """LLM provider configuration."""

    # OpenAI configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Azure OpenAI configuration
    azure_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
    azure_deployments: Dict[str, str] = {}  # Model name to deployment name mapping
    
    # Groq configuration
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    
    # Parse Azure deployment mapping from environment if available
    def __init__(self, **data):
        super().__init__(**data)
        # Try to parse Azure deployments from environment variables
        azure_deployments_str = os.getenv("AZURE_OPENAI_DEPLOYMENTS", "")
        if azure_deployments_str:
            try:
                # Format: "gpt-3.5-turbo:deployment1,gpt-4:deployment2"
                pairs = azure_deployments_str.split(",")
                for pair in pairs:
                    if ":" in pair:
                        model, deployment = pair.split(":", 1)
                        self.azure_deployments[model.strip()] = deployment.strip()
            except Exception:
                # In case of parsing error, just keep empty dict
                pass

llm_config=LLMConfig()