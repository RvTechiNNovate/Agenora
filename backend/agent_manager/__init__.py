# agent_manager/__init__.py
"""
Agent manager package that provides interfaces for different agent frameworks.
"""
from backend.agent_manager.manager import agent_provider_manager

# Export the providers and default provider
managers = agent_provider_manager.providers
