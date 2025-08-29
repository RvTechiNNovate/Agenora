"""
Backend package initializer.
Import all models to ensure they're registered with the Base metadata.
"""
# Import all models from the centralized models file
from backend.database import Base
from backend.models import AgentModel, CrewAIAgentModel, LangChainAgentModel, AgnoAgentModel, AgentVersionModel, SettingModel
