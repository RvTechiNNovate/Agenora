from fastapi import APIRouter, Request, Depends, HTTPException, status
from backend.core.logging import get_logger
from backend.utils.security import verify_api_key
from backend.services.agent_service import AgentService
from backend.schemas.schemas import QueryRequest, QueryResponse


# Set up logging
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["agent execution"])

@router.post("/agent/{agent_id}/start",
         dependencies=[Depends(verify_api_key)],
         summary="Start an agent",
         description="Start a specific agent to prepare it for processing queries.")
async def start_agent(agent_id: int):
    """Start an agent by ID."""
    logger.info(f"Attempting to start agent {agent_id}")
    
    # Use service layer for business logic
    result = AgentService.start_agent(agent_id)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return {"status": result["status"], "message": result.get("message")}

@router.post("/agent/{agent_id}/stop",
         dependencies=[Depends(verify_api_key)],
         summary="Stop an agent",
         description="Stop a running agent.")
async def stop_agent(agent_id: int):
    """Stop an agent by ID."""
    logger.info(f"Attempting to stop agent {agent_id}")
    
    # Use service layer for business logic
    result = AgentService.stop_agent(agent_id)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return {"status": result["status"], "message": result.get("message")}


@router.post("/agent/{agent_id}/query",
         dependencies=[Depends(verify_api_key)],
         response_model=QueryResponse,
         summary="Query an agent",
         description="Send a query to a running agent and get a response.")
async def query_agent(agent_id: int, query_req: QueryRequest, request: Request):
    """Query a running agent."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Query for agent {agent_id} from {client_ip}: {query_req.query[:50]}...")
    
    # Use service layer for business logic
    result = AgentService.query_agent(agent_id, query_req.query)
    
    # Handle service response
    if not result["success"]:
        raise HTTPException(
            status_code=result["status_code"],
            detail=result["error"]
        )
    
    return {"response": result["response"]}
