"""
MCP Tools manager for discovering and using MCP service tools.
"""
import json
import requests
from typing import List, Dict, Any, Optional
import logging

from backend.core.logging import get_logger

# Set up logger
logger = get_logger(__name__)

class MCPToolAdapter:
    """Adapter for MCP tools to be used with different agent frameworks."""
    
    def __init__(self, tool_data: Dict[str, Any]):
        """
        Initialize an MCP tool adapter.
        
        Args:
            tool_data: Raw tool data from MCP service
        """
        self.name = tool_data.get("name", "")
        self.description = tool_data.get("description", "")
        self.parameters = tool_data.get("parameters", {})
        self.mcp_service_url = tool_data.get("service_url", "")
        self.tool_id = tool_data.get("tool_id", "")
        self.raw_data = tool_data
        
    def to_langchain_format(self) -> Dict[str, Any]:
        """Convert to LangChain tool format."""
        # Implement conversion logic for LangChain tools
        return {
            "name": self.name,
            "description": self.description,
            # Add other necessary fields for LangChain tools
        }
        
    def to_crewai_format(self) -> Dict[str, Any]:
        """Convert to CrewAI tool format."""
        # Implement conversion logic for CrewAI tools
        return {
            "name": self.name,
            "description": self.description,
            # Add other necessary fields for CrewAI tools
        }
        
    def to_langgraph_format(self) -> Dict[str, Any]:
        """Convert to LangGraph tool format."""
        # Implement conversion logic for LangGraph tools
        return {
            "name": self.name,
            "description": self.description,
            # Add other necessary fields for LangGraph tools
        }
        
    def execute(self, **params) -> Any:
        """
        Execute the MCP tool with the given parameters.
        
        Args:
            **params: Parameters to pass to the MCP tool
            
        Returns:
            Tool execution result
        """
        try:
            # Make request to MCP service
            response = requests.post(
                f"{self.mcp_service_url}/api/tools/{self.tool_id}/execute",
                json=params,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error executing MCP tool {self.name}: {str(e)}")
            return {"error": str(e)}


class MCPToolsManager:
    """Manager for MCP tools discovery and execution."""
    
    def __init__(self):
        """Initialize MCP tools manager."""
        self.mcp_services = []  # List of registered MCP service URLs
        self.available_tools = {}  # Map of tool_id to MCPToolAdapter
        
    def register_mcp_service(self, service_url: str) -> bool:
        """
        Register an MCP service for tool discovery.
        
        Args:
            service_url: URL of the MCP service
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Check if service is valid and available
            response = requests.get(
                f"{service_url}/api/info",
                timeout=5
            )
            response.raise_for_status()
            
            # Add to services list if not already present
            if service_url not in self.mcp_services:
                self.mcp_services.append(service_url)
                
            # Discover tools from this service
            self._discover_tools(service_url)
            return True
            
        except Exception as e:
            logger.error(f"Error registering MCP service {service_url}: {str(e)}")
            return False
            
    def unregister_mcp_service(self, service_url: str) -> bool:
        """
        Unregister an MCP service.
        
        Args:
            service_url: URL of the MCP service to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        try:
            # Remove from services list
            if service_url in self.mcp_services:
                self.mcp_services.remove(service_url)
                
            # Remove tools from this service
            self._remove_service_tools(service_url)
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering MCP service {service_url}: {str(e)}")
            return False
            
    def _discover_tools(self, service_url: str) -> None:
        """
        Discover tools from an MCP service.
        
        Args:
            service_url: URL of the MCP service
        """
        try:
            # Get tools from MCP service
            response = requests.get(
                f"{service_url}/api/tools",
                timeout=10
            )
            response.raise_for_status()
            
            tools_data = response.json().get("tools", [])
            
            # Add tools to available tools
            for tool_data in tools_data:
                tool_data["service_url"] = service_url
                tool_id = f"{service_url}:{tool_data.get('name')}"
                tool_data["tool_id"] = tool_id
                
                self.available_tools[tool_id] = MCPToolAdapter(tool_data)
                
            logger.info(f"Discovered {len(tools_data)} tools from {service_url}")
            
        except Exception as e:
            logger.error(f"Error discovering tools from {service_url}: {str(e)}")
            
    def _remove_service_tools(self, service_url: str) -> None:
        """
        Remove all tools from a specific service.
        
        Args:
            service_url: URL of the MCP service
        """
        # Remove tools with matching service URL
        tools_to_remove = [
            tool_id for tool_id, tool in self.available_tools.items()
            if tool.mcp_service_url == service_url
        ]
        
        for tool_id in tools_to_remove:
            del self.available_tools[tool_id]
            
        logger.info(f"Removed {len(tools_to_remove)} tools from {service_url}")
            
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get all available MCP tools.
        
        Returns:
            List of tool information dictionaries
        """
        return [
            {
                "id": tool_id,
                "name": tool.name,
                "description": tool.description,
                "service_url": tool.mcp_service_url
            }
            for tool_id, tool in self.available_tools.items()
        ]
        
    def get_tool_details(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tool.
        
        Args:
            tool_id: ID of the tool
            
        Returns:
            Dictionary with tool details or None if not found
        """
        tool = self.available_tools.get(tool_id)
        if not tool:
            return None
            
        return {
            "id": tool_id,
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "service_url": tool.mcp_service_url,
            "raw_data": tool.raw_data
        }
        
    def execute_tool(self, tool_id: str, params: Dict[str, Any]) -> Any:
        """
        Execute an MCP tool.
        
        Args:
            tool_id: ID of the tool to execute
            params: Parameters to pass to the tool
            
        Returns:
            Tool execution result
        """
        tool = self.available_tools.get(tool_id)
        if not tool:
            return {"error": f"Tool {tool_id} not found"}
            
        return tool.execute(**params)
        
    def refresh_tools(self) -> None:
        """Refresh all tools from registered MCP services."""
        for service_url in self.mcp_services:
            self._discover_tools(service_url)
            
    def get_tools_for_framework(self, framework: str) -> List[Dict[str, Any]]:
        """
        Get tools adapted for a specific agent framework.
        
        Args:
            framework: Name of the agent framework (langchain, crewai, etc.)
            
        Returns:
            List of tools in the format expected by the framework
        """
        result = []
        
        for tool in self.available_tools.values():
            if framework == "langchain":
                result.append(tool.to_langchain_format())
            elif framework == "crewai":
                result.append(tool.to_crewai_format())
            elif framework == "langgraph":
                result.append(tool.to_langgraph_format())
            # Add other frameworks as needed
            
        return result


# Create a singleton instance
mcp_tools_manager = MCPToolsManager()
