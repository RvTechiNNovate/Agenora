# API Documentation

This document provides an overview of the Agenora API endpoints.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8000/api
```

## Authentication

Some endpoints require authentication. Include an API key in the `X-API-KEY` header:

```
X-API-KEY: your_api_key_here
```

## Agent Endpoints

### List Agents

Get a list of all agents.

```
GET /agents
```

#### Response

```json
{
  "agents": [
    {
      "id": 1,
      "name": "Research Assistant",
      "description": "Helps with research tasks",
      "framework": "crewai",
      "status": "stopped",
      "model": "openai:gpt-4",
      "created_at": "2025-08-25T12:34:56"
    },
    ...
  ]
}
```

### Create Agent

Create a new agent.

```
POST /agent
```

#### Request Body

```json
{
  "name": "Customer Support Agent",
  "description": "Handles customer inquiries",
  "framework": "crewai",
  "model": "openai:gpt-4",
  "model_config": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "role": "Customer Support Specialist",
  "backstory": "You are an experienced customer support specialist...",
  "task": "Answer customer questions about our products",
  "expected_output": "Helpful and accurate responses"
}
```

#### Response

```json
{
  "id": 2,
  "name": "Customer Support Agent",
  "status": "stopped",
  "message": "Agent created successfully"
}
```

### Get Agent Details

Get details about a specific agent.

```
GET /agent/{agent_id}
```

#### Response

```json
{
  "id": 2,
  "name": "Customer Support Agent",
  "description": "Handles customer inquiries",
  "framework": "crewai",
  "status": "stopped",
  "model": "openai:gpt-4",
  "model_config": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "role": "Customer Support Specialist",
  "backstory": "You are an experienced customer support specialist...",
  "task": "Answer customer questions about our products",
  "expected_output": "Helpful and accurate responses",
  "created_at": "2025-08-25T13:45:00"
}
```

### Start Agent

Start a specific agent.

```
POST /agent/{agent_id}/start
```

#### Response

```json
{
  "id": 2,
  "status": "running",
  "message": "Agent started successfully"
}
```

### Stop Agent

Stop a specific agent.

```
POST /agent/{agent_id}/stop
```

#### Response

```json
{
  "id": 2,
  "status": "stopped",
  "message": "Agent stopped successfully"
}
```

### Query Agent

Send a query to a specific agent.

```
POST /agent/{agent_id}/query
```

#### Request Body

```json
{
  "query": "Tell me about your product pricing"
}
```

#### Response

```json
{
  "response": "Our product pricing is structured as follows...",
  "metadata": {
    "tokens_used": 145,
    "response_time": 1.23
  }
}
```

### Update Agent

Update a specific agent's configuration.

```
PUT /agent/{agent_id}
```

#### Request Body

```json
{
  "name": "Updated Agent Name",
  "description": "Updated description",
  "model_config": {
    "temperature": 0.5
  }
}
```

#### Response

```json
{
  "id": 2,
  "status": "stopped",
  "message": "Agent updated successfully"
}
```

### Delete Agent

Delete a specific agent.

```
DELETE /agent/{agent_id}
```

#### Response

```json
{
  "id": 2,
  "message": "Agent deleted successfully"
}
```

## Framework Endpoints

### List Available Frameworks

Get a list of available agent frameworks.

```
GET /frameworks
```

#### Response

```json
{
  "frameworks": [
    {
      "name": "crewai",
      "display_name": "CrewAI",
      "description": "Multi-agent framework for creating agent teams",
      "schema": {
        "fields": {
          "role": "string",
          "backstory": "string",
          "task": "string",
          "expected_output": "string"
        }
      }
    },
    ...
  ]
}
```

## System Endpoints

### Get System Status

Get system status information.

```
GET /system/status
```

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "2d 3h 45m",
  "active_agents": 3,
  "total_agents": 10,
  "system_load": {
    "cpu": 23.5,
    "memory": 42.1
  }
}
```

### Get API Key

Generate a new API key.

```
POST /system/api-key
```

#### Request Body

```json
{
  "name": "My Application",
  "expires_in_days": 30
}
```

#### Response

```json
{
  "api_key": "ak_1234567890abcdef",
  "name": "My Application",
  "expires_at": "2025-09-25T00:00:00"
}
```

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": {
    "code": "agent_not_found",
    "message": "Agent with ID 123 not found"
  }
}
```

Common HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
