"""
API routes for MCP tools operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any

from backend.core.config import config
from backend.utils.security import verify_api_key
from backend.services.mcp_tools_service import MCPToolsService

# Create router
router = APIRouter(prefix="/api", tags=["mcp-tools"])

@router.post("/mcp/services",
        summary="Register an MCP service",
        description="Register a new MCP service for tool discovery.")
async def register_mcp_service(service_data: Dict[str, str]):
    """Register a new MCP service."""
    if "url" not in service_data:
        raise HTTPException(status_code=400, detail="Service URL is required")
        
    result = MCPToolsService.register_mcp_service(service_data["url"])
    
    if not result.get("success", False):
        status_code = result.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=result.get("error", "Unknown error"))
        
    return result

@router.delete("/mcp/services",
        summary="Unregister an MCP service",
        description="Unregister an existing MCP service.")
async def unregister_mcp_service(service_data: Dict[str, str]):
    """Unregister an MCP service."""
    if "url" not in service_data:
        raise HTTPException(status_code=400, detail="Service URL is required")
        
    result = MCPToolsService.unregister_mcp_service(service_data["url"])
    
    if not result.get("success", False):
        status_code = result.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=result.get("error", "Unknown error"))
        
    return result

@router.get("/mcp/services",
        summary="Get registered MCP services",
        description="Get all registered MCP services.")
async def get_mcp_services():
    """Get all registered MCP services."""
    try:
        return MCPToolsService.get_registered_mcp_services()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting MCP services: {str(e)}")

@router.get("/mcp/tools",
        summary="Get available MCP tools",
        description="Get all available MCP tools from registered services.")
async def get_mcp_tools():
    """Get all available MCP tools."""
    try:
        return MCPToolsService.get_available_tools()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting MCP tools: {str(e)}")

@router.get("/mcp/tools/{tool_id}",
        summary="Get tool details",
        description="Get detailed information about a specific MCP tool.")
async def get_tool_details(tool_id: str):
    """Get detailed information about a specific tool."""
    result = MCPToolsService.get_tool_details(tool_id)
    
    if "error" in result:
        status_code = result.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=result["error"])
        
    return result

@router.post("/mcp/tools/{tool_id}/execute",
        summary="Execute MCP tool",
        description="Execute a specific MCP tool with the given parameters.")
async def execute_tool(tool_id: str, params: Dict[str, Any]):
    """Execute an MCP tool."""
    result = MCPToolsService.execute_tool(tool_id, params)
    
    if "error" in result:
        status_code = result.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=result["error"])
        
    return result

@router.post("/mcp/tools/refresh",
        summary="Refresh MCP tools",
        description="Refresh all tools from registered MCP services.")
async def refresh_tools():
    """Refresh all tools from registered MCP services."""
    result = MCPToolsService.refresh_tools()
    
    if not result.get("success", False):
        status_code = result.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=result.get("error", "Unknown error"))
        
    return result

@router.get("/mcp/tools/frameworks/{framework}",
        summary="Get MCP tools for framework",
        description="Get tools adapted for a specific agent framework.")
async def get_tools_for_framework(framework: str):
    """Get tools adapted for a specific agent framework."""
    result = MCPToolsService.get_tools_for_framework(framework)
    
    if "error" in result:
        status_code = result.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=result["error"])
        
    return result
