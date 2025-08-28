import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base, get_db

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_list_agents_empty():
    """Test listing agents when there are none."""
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert response.json() == {}

def test_create_agent():
    """Test creating a new agent."""
    agent_data = {
        "name": "Test Agent",
        "description": "A test agent",
        "role": "Tester",
        "model": "gpt-3.5-turbo"
    }
    
    response = client.post("/api/agent", json=agent_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "agent_id" in data
    assert data["agent"]["name"] == "Test Agent"
    assert data["agent"]["status"] == "stopped"

def test_get_agent():
    """Test getting details for a specific agent."""
    # First create an agent
    agent_data = {
        "name": "Agent to Fetch",
        "description": "An agent to test fetching",
        "role": "Tester",
        "model": "gpt-3.5-turbo"
    }
    
    create_response = client.post("/api/agent", json=agent_data)
    agent_id = create_response.json()["agent_id"]
    
    # Now fetch the agent
    response = client.get(f"/api/agent/{agent_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Agent to Fetch"
    
def test_nonexistent_agent():
    """Test getting a nonexistent agent."""
    response = client.get("/api/agent/999")
    assert response.status_code == 404
