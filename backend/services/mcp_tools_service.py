"""
MCP tools service module for business logic related to MCP tool operations.
"""
from typing import Dict, List, Any, Optional
from backend.core.logging import get_logger
from backend.mcp_tools.manager import mcp_tools_manager

logger = get_logger(__name__)


class MCPToolsService:
    """Service class for MCP tools-related business operations."""
    
    @staticmethod
    def register_mcp_service(service_url: str) -> Dict[str, Any]:
        """
        Register an MCP service for tool discovery.
        
        Args:
            service_url: URL of the MCP service
            
        Returns:
            Dict containing success status and message
        """
        try:
            success = mcp_tools_manager.register_mcp_service(service_url)
            
            if success:
                return {
                    "success": True,
                    "message": f"Successfully registered MCP service at {service_url}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to register MCP service at {service_url}",
                    "status_code": 400
                }
                
        except Exception as e:
            logger.error(f"Error registering MCP service: {str(e)}")
            return {
                "success": False,
                "error": f"Error registering MCP service: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def unregister_mcp_service(service_url: str) -> Dict[str, Any]:
        """
        Unregister an MCP service.
        
        Args:
            service_url: URL of the MCP service to unregister
            
        Returns:
            Dict containing success status and message
        """
        try:
            success = mcp_tools_manager.unregister_mcp_service(service_url)
            
            if success:
                return {
                    "success": True,
                    "message": f"Successfully unregistered MCP service at {service_url}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to unregister MCP service at {service_url}",
                    "status_code": 400
                }
                
        except Exception as e:
            logger.error(f"Error unregistering MCP service: {str(e)}")
            return {
                "success": False,
                "error": f"Error unregistering MCP service: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def get_registered_mcp_services() -> Dict[str, Any]:
        """
        Get all registered MCP services.
        
        Returns:
            Dict containing list of registered service URLs
        """
        try:
            return {
                "services": mcp_tools_manager.mcp_services
            }
                
        except Exception as e:
            logger.error(f"Error getting registered MCP services: {str(e)}")
            return {
                "error": f"Error getting registered MCP services: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def get_available_tools() -> Dict[str, Any]:
        """
        Get all available MCP tools.
        
        Returns:
            Dict containing list of available tools
        """
        try:
            tools = mcp_tools_manager.get_available_tools()
            return {
                "tools": tools,
                "count": len(tools)
            }
                
        except Exception as e:
            logger.error(f"Error getting available MCP tools: {str(e)}")
            return {
                "error": f"Error getting available MCP tools: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def get_tool_details(tool_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific tool.
        
        Args:
            tool_id: ID of the tool
            
        Returns:
            Dict containing tool details
        """
        try:
            tool = mcp_tools_manager.get_tool_details(tool_id)
            
            if tool:
                return tool
            else:
                return {
                    "error": f"Tool {tool_id} not found",
                    "status_code": 404
                }
                
        except Exception as e:
            logger.error(f"Error getting tool details: {str(e)}")
            return {
                "error": f"Error getting tool details: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def execute_tool(tool_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool.
        
        Args:
            tool_id: ID of the tool to execute
            params: Parameters to pass to the tool
            
        Returns:
            Dict containing tool execution result
        """
        try:
            result = mcp_tools_manager.execute_tool(tool_id, params)
            
            if "error" in result:
                return {
                    "error": result["error"],
                    "status_code": 400
                }
            
            return {
                "result": result
            }
                
        except Exception as e:
            logger.error(f"Error executing MCP tool: {str(e)}")
            return {
                "error": f"Error executing MCP tool: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def refresh_tools() -> Dict[str, Any]:
        """
        Refresh all tools from registered MCP services.
        
        Returns:
            Dict containing success status and message
        """
        try:
            mcp_tools_manager.refresh_tools()
            
            return {
                "success": True,
                "message": "Successfully refreshed MCP tools",
                "tools_count": len(mcp_tools_manager.available_tools)
            }
                
        except Exception as e:
            logger.error(f"Error refreshing MCP tools: {str(e)}")
            return {
                "success": False,
                "error": f"Error refreshing MCP tools: {str(e)}",
                "status_code": 500
            }
    
    @staticmethod
    def get_tools_for_framework(framework: str) -> Dict[str, Any]:
        """
        Get tools adapted for a specific agent framework.
        
        Args:
            framework: Name of the agent framework (langchain, crewai, etc.)
            
        Returns:
            Dict containing list of tools for the framework
        """
        try:
            tools = mcp_tools_manager.get_tools_for_framework(framework)
            
            return {
                "framework": framework,
                "tools": tools,
                "count": len(tools)
            }
                
        except Exception as e:
            logger.error(f"Error getting tools for framework {framework}: {str(e)}")
            return {
                "error": f"Error getting tools for framework {framework}: {str(e)}",
                "status_code": 500
            }
