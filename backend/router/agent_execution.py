from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.config import config
from backend.database import get_db, AgentModel
from backend.utils.logging import get_logger
from backend.utils.security import verify_api_key
from backend.agent_manager import managers

# Set up logging
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["agent execution"])

@router.post("/agent/{agent_id}/start",
         dependencies=[Depends(verify_api_key)],
         summary="Start an agent",
         description="Start a specific agent to prepare it for processing queries.")
async def start_agent(agent_id: int, db: Session = Depends(get_db)):
    """Start an agent by ID."""
    logger.info(f"Attempting to start agent {agent_id}")
    
    # Find the agent in the database to determine which framework to use
    agent_db = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Get the appropriate manager
    framework = agent_db.framework
    if framework in managers:
        manager = managers[framework]
    else:
        logger.warning(f"Framework {framework} not supported, using default manager")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework {framework} not supported. Try creating agent using available frameworks."
        )
    
    # Start the agent
    success = manager.start_agent(agent_id)
    logger.info(f"Agent {agent_id} start result: {success}")
    
    if success:
        return {"status": "started"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Agent not found or failed to start"
    )

@router.post("/agent/{agent_id}/stop",
         dependencies=[Depends(verify_api_key)],
         summary="Stop an agent",
         description="Stop a running agent.")
async def stop_agent(agent_id: int, db: Session = Depends(get_db)):
    """Stop an agent by ID."""
    # Find the agent in the database to determine which framework to use
    agent_db = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Get the appropriate manager
    framework = agent_db.framework
    if framework in managers:
        manager = managers[framework]
    else:
        logger.warning(f"Framework {framework} not supported, using default manager")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework {framework} not supported. Try creating agent using available frameworks."
        )

    success = manager.stop_agent(agent_id)
    
    if success:
        return {"status": "stopped"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Agent not found"
    )

# API Models for query functionality
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """Request model for querying an agent."""
    query: str = Field(..., description="The query text to send to the agent")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "query": "What are the latest trends in artificial intelligence?"
            }
        }

@router.post("/agent/{agent_id}/query",
         dependencies=[Depends(verify_api_key)],
         summary="Query an agent",
         description="Send a query to a running agent and get a response.")
async def query_agent(agent_id: int, query_req: QueryRequest, request: Request, db: Session = Depends(get_db)):
    """Query a running agent."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Query for agent {agent_id} from {client_ip}: {query_req.query[:50]}...")
    
    # Validate query length
    if len(query_req.query) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query too long. Maximum length is 100 characters."
        )
    
    # Find the agent in the database to determine which framework to use
    agent_db = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Get the appropriate manager
    framework = agent_db.framework
    if framework in managers:
        manager = managers[framework]
    else:
        logger.warning(f"Framework {framework} not supported, using default manager")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework {framework} not supported. Try creating agent using available frameworks."
        )
    
    result = manager.query_agent(agent_id, query_req.query)
    
    if "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        elif "not running" in result["error"].lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
    
    return result
