from fastapi import  Request, Depends, HTTPException, status
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.schemas.schemas import AgentCreateResponse
from backend.core.logging import get_logger
from backend.utils.security import verify_api_key
from backend.services.agent_service import AgentService


# Set up logging
logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["agents"])

@router.post("/agent", 
         response_model=AgentCreateResponse,
         dependencies=[Depends(verify_api_key)],
         summary="Create a new agent",
         description="Create a new agent with the specified configuration.",
         status_code=status.HTTP_201_CREATED)
async def create_agent(request: Request):
    """Create a new agent with the given configuration."""
    # Parse request body
    data = await request.json()
    
    client_ip = request.client.host if request.client else "unknown"
    framework = data.get("framework", "").lower()
    logger.info(f"Create agent request from {client_ip} for framework: {framework}")
    
    # Use service layer for business logic
    result = AgentService.create_agent(data)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return {
        "agent_id": result["agent_id"],
        "agent": result["agent"]
    }

@router.get("/agents", 
        dependencies=[Depends(verify_api_key)],
        summary="List all agents",
        description="Get a list of all created agents with their status.",
        status_code=status.HTTP_200_OK)
async def list_agents():
    """List all agents in the system."""
    # Use service layer
    result = AgentService.get_all_agents()
    
    # Return agents or empty dict if failed
    return result.get("agents", {})
@router.get("/agent/{agent_id}", 
        dependencies=[Depends(verify_api_key)],
        summary="Get agent details",
        description="Get detailed information about a specific agent.",
        status_code=status.HTTP_200_OK)
async def get_agent(agent_id: int):
    """Get detailed information about a specific agent."""
    # Use service layer
    result = AgentService.get_agent_by_id(agent_id)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return result["agent"]

@router.put("/agent/{agent_id}",
        dependencies=[Depends(verify_api_key)],
        summary="Update an agent",
        description="Update a specific agent's configuration.")
async def update_agent(agent_id: int, request: Request):
    """Update an agent by ID."""
    logger.info(f"Attempting to update agent {agent_id}")
    
    # Parse request body
    data = await request.json()
    
    # Use service layer
    result = AgentService.update_agent(agent_id, data)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return {
        "agent_id": result["agent_id"],
        "agent": result["agent"]
    }


@router.delete("/agent/{agent_id}",
         dependencies=[Depends(verify_api_key)],
         summary="Delete an agent",
         description="Permanently delete an agent and all associated resources.")
async def delete_agent(agent_id: int):
    """Delete an agent by ID."""
    logger.info(f"Attempting to delete agent {agent_id}")
    
    # Use service layer
    result = AgentService.delete_agent(agent_id)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return {
        "status": result["status"],
        "message": result["message"]
    }


@router.get("/agent/{agent_id}/versions", 
        dependencies=[Depends(verify_api_key)],
        summary="Get agent version history",
        description="Get the version history for a specific agent.")
async def get_agent_versions(agent_id: int):
    """Get version history for an agent."""
    # Use service layer
    result = AgentService.get_agent_versions(agent_id)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return {"versions": result["versions"]}

@router.post("/agent/{agent_id}/restore/{version_number}", 
        dependencies=[Depends(verify_api_key)],
        summary="Restore agent version",
        description="Restore an agent to a previous version.")
async def restore_agent_version(agent_id: int, version_number: int):
    """Restore an agent to a previous version."""
    # Use service layer
    result = AgentService.restore_agent_version(agent_id, version_number)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return {
        "agent_id": result["agent_id"],
        "message": result["message"],
        "agent": result["agent"]
    }

