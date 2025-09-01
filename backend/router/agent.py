from fastapi import  Request, Depends, HTTPException, status
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.schemas import AgentCreateResponse
from backend.database import  get_db
from backend.models import AgentModel, AgentVersionModel
from backend.utils.logging import get_logger
from backend.utils.security import verify_api_key
from backend.agent_manager import managers


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
    
    # Validate framework first
    if "framework" not in data:
        raise HTTPException(status_code=400, detail="Framework must be specified")
    
    framework = data.get("framework").lower()
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Create agent request from {client_ip} for framework: {framework}")
    
    # Validate common fields first
    required_fields = ["name", "description", "model"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    try:

        # Convert to dict to pass to manager
        task_dict = data
        
        # Rename the field for compatibility with the manager
        if task_dict.get("model_settings"):
            task_dict["model_config"] = task_dict.pop("model_settings")
        
        # TODO
        if framework=="crewai":
            task_dict["expected_output"] = data.get("expected_output","Sort response")
        
        # Get the appropriate manager for the framework
        if framework in managers:
            framework_manager = managers[framework]
        else:
            logger.warning(f"Framework {framework} not supported, using default manager")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Framework {framework} not supported. Try creating agent using available frameworks."
            )
        
        # Use the manager's validation method if available
        if hasattr(framework_manager, 'validate_agent_config'):
            validation_result = framework_manager.validate_agent_config(task_dict)
            if validation_result is not True:
                logger.warning(f"Agent validation failed: {validation_result}")
                raise HTTPException(status_code=400, detail=f"Invalid agent configuration: {validation_result}")
        
        # Create agent using the selected manager
        agent_id = framework_manager.create_agent(task_dict)
        
        logger.info(f"Created agent {agent_id} with name {task_dict['name']}")
        
        return {
            "agent_id": agent_id, 
            "agent": {
                    "id": agent_id,
                    "name": task_dict["name"],
                    "description": task_dict["description"],
                    "framework": task_dict["framework"],
                    "status": "stopped",
                    "model": task_dict["model"]
                }
            }
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )

@router.get("/agents", 
        dependencies=[Depends(verify_api_key)],
        summary="List all agents",
        description="Get a list of all created agents with their status.",
        status_code=status.HTTP_200_OK)
async def list_agents():
    """List all agents in the system."""
    # Combine agents from all managers
    all_agents = {}
    for framework, manager in managers.items():
        framework_agents = manager.get_all_agents()
        all_agents.update(framework_agents)
    
    return all_agents
@router.get("/agent/{agent_id}", 
        dependencies=[Depends(verify_api_key)],
        summary="Get agent details",
        description="Get detailed information about a specific agent.",
        status_code=status.HTTP_200_OK)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific agent."""
    
    
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    return agent.to_dict()

@router.put("/agent/{agent_id}",
        dependencies=[Depends(verify_api_key)],
        summary="Update an agent",
        description="Update a specific agent's configuration.")
async def update_agent(agent_id: int, request: Request, db: Session = Depends(get_db)):
    """Update an agent by ID."""
    logger.info(f"Attempting to update agent {agent_id}")
    
    # Parse request body
    data = await request.json()
    
    # Get the agent to determine its framework
    
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Get the framework, defaulting to the agent's current framework
    framework = data.get("framework") or agent.framework
    
    # Apply framework-specific logic
    try:
        # Validate common fields
        for field in ["name", "description"]:
            if field in data and not data[field]:
                raise HTTPException(status_code=400, detail=f"Field cannot be empty: {field}")
        
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=400, detail=f"Invalid input for framework {framework}: {str(e)}")
        else:
            raise
    
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
    
    # Before updating, create a version of the current state
    
    current_version = agent_db.version
    new_version = AgentVersionModel.from_dict(agent_db, current_version)
    db.add(new_version)
    
    # Use the data dict to pass to manager
    task_dict = data
    
    # Rename the field back for compatibility with the manager
    if task_dict.get("model_settings"):
        task_dict["model_config"] = task_dict.pop("model_settings")
    
    # Use the manager's validation method if available
    if hasattr(manager, 'validate_agent_config'):
        # For update, we may need to get the current config and merge with changes
        current_config = agent_db.to_dict()
        # Merge current with updates, giving priority to updates
        merged_config = {**current_config, **task_dict}
        validation_result = manager.validate_agent_config(merged_config)
        if validation_result is not True:
            logger.warning(f"Agent validation failed: {validation_result}")
            raise HTTPException(status_code=400, detail=f"Invalid agent configuration: {validation_result}")
    
    # Update the agent
    success = manager.update_agent(agent_id, task_dict)
    
    if success:
        # Increment the version number
        updated_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        updated_agent.version = current_version + 1
        db.commit()
        
        return {
            "agent_id": agent_id,
            "agent": {
                "id": agent_id,
                "name": updated_agent.name,
                "description": updated_agent.description,
                "framework": updated_agent.framework,
                "status": updated_agent.status,
                "model": updated_agent.model,
                "version": updated_agent.version
            }
        }
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to update agent"
    )


@router.delete("/agent/{agent_id}",
         dependencies=[Depends(verify_api_key)],
         summary="Delete an agent",
         description="Permanently delete an agent and all associated resources.")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Delete an agent by ID."""
    logger.info(f"Attempting to delete agent {agent_id}")
    
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
    
    success = manager.delete_agent(agent_id)
    
    if success:
        return {"status": "deleted", "message": f"Agent {agent_id} deleted successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete agent"
    )


@router.get("/agent/{agent_id}/versions", 
        dependencies=[Depends(verify_api_key)],
        summary="Get agent version history",
        description="Get the version history for a specific agent.")
async def get_agent_versions(agent_id: int, db: Session = Depends(get_db)):
    """Get version history for an agent."""
    
    
    # Check if agent exists
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Get all versions for this agent
    versions = db.query(AgentVersionModel).filter(
        AgentVersionModel.agent_id == agent_id
    ).order_by(AgentVersionModel.version_number.desc()).all()
    
    # Include current version as well
    current_version = {
        "id": None,  # No version ID for current state
        "agent_id": agent.id,
        "version_number": agent.version,
        "name": agent.name,
        "description": agent.description,
        "framework": agent.framework,
        "model": agent.model,
        "created_at": agent.updated_at.isoformat() if agent.updated_at else None,
        "is_current": True
    }
    
    # Format the response
    version_history = [current_version] + [
        {**v.to_dict(), "is_current": False} 
        for v in versions
    ]
    
    return {"versions": version_history}

@router.post("/agent/{agent_id}/restore/{version_number}", 
        dependencies=[Depends(verify_api_key)],
        summary="Restore agent version",
        description="Restore an agent to a previous version.")
async def restore_agent_version(agent_id: int, version_number: int, db: Session = Depends(get_db)):
    """Restore an agent to a previous version."""
    
    # Check if agent exists
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Get the specified version
    version = db.query(AgentVersionModel).filter(
        AgentVersionModel.agent_id == agent_id,
        AgentVersionModel.version_number == version_number
    ).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} for agent {agent_id} not found"
        )
    
    # Create a new version based on current state before restoring
    current_version = AgentVersionModel.from_dict(agent, agent.version)
    db.add(current_version)
    
    # Restore the agent to the specified version
    agent.name = version.name
    agent.description = version.description
    agent.framework = version.framework
    agent.role = version.role
    agent.backstory = version.backstory
    agent.task = version.task
    agent.model = version.model
    agent.model_config = version.model_config
    agent.version = agent.version + 1  # Increment version number
    
    db.commit()
    
    # Get the right manager for this framework
    framework = agent.framework
    if framework in managers:
        manager = managers[framework]
    else:
        logger.warning(f"Framework {framework} not supported, using default manager")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework {framework} not supported. Try creating agent using available frameworks."
        )
    
    # Update the manager's cache
    if agent.id in manager.agents:
        manager.agents[agent.id]["config"] = agent.to_dict()
    
    return {
        "agent_id": agent_id,
        "message": f"Agent restored to version {version_number}",
        "agent": agent.to_dict()
    }

