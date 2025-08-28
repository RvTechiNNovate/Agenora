
# 🏗️ Agent Dashboard Architecture

This document explains the high-level architecture of the **Agent Dashboard** project.

---

## ⚡ Overview

The system provides a **web dashboard** for creating, managing, and interacting with AI agents.  
It is designed to be **modular, extensible, and production-ready**, supporting multiple frameworks like **CrewAI** (current) and **LangChain** (future).

---

## 🔲 System Components

### 1. **Frontend**
- Located in `frontend/`
- Provides the **web UI** for:
  - Agent creation (forms for roles, tasks, models)
  - Playground (chat interface with agents)
  - Monitoring running agents
- Built with HTML/CSS/JS (can later migrate to React/Vue)

### 2. **Backend**
- Located in `backend/`
- Powered by **FastAPI**
- Responsibilities:
  - Expose REST APIs for agent management
  - Serve the playground endpoints
  - Handle authentication & authorization
  - Persist agent data in the database

#### API Layer
- Implemented in `main.py`
- Defines routes like `/api/agent`, `/api/agent/{id}/start`, etc.

#### Service Layer
- Implemented in `backend/agent_manager/`
- Contains **framework-specific managers** (e.g., `CrewAIManager`)
- Each manager implements a common interface so the system can switch frameworks easily

#### Data Layer
- Implemented in `backend/database.py`
- Uses **SQLAlchemy ORM**
- Stores agent configs, states, and logs

#### Configuration Layer
- `backend/config.py`
- Loads settings from `.env` (API keys, database URL, etc.)
- Makes the system portable between dev, staging, and prod

### 3. **Database**
- Configurable via `DATABASE_URL`
- Default: **SQLite** (for local dev)
- Supports migration to **PostgreSQL** or other RDBMS in production

### 4. **Agents**
- Created and managed via API/UI
- Configurations include:
  - Name, role, backstory
  - Model provider (OpenAI, Anthropic, etc.)
  - Parameters (temperature, max tokens)
- Agent lifecycle:
  1. Create agent (persist config in DB)
  2. Start agent (run through selected manager)
  3. Query agent (through playground or API)
  4. Stop agent (terminate process/session)

---

## 🔄 Workflow

1. **User creates an agent** via UI → request goes to backend API → agent config is stored in DB.  
2. **User starts agent** → backend loads agent config → spins up via framework manager (CrewAI).  
3. **User queries agent** → request passes through FastAPI → forwarded to agent → response returned to UI.  
4. **User stops agent** → backend terminates agent session → updates status in DB.  

---

## 📂 Clean Architecture Layers

- **Presentation Layer** → Frontend (UI)  
- **API Layer** → FastAPI routes  
- **Service Layer** → Agent managers (CrewAI, LangChain, …)  
- **Data Layer** → SQLAlchemy models & DB  
- **Infrastructure** → Config, logging, Docker  

---

## 🔌 Extensibility

Adding a new agent framework:
1. Create `backend/agent_manager/NewFrameworkManager.py`
2. Implement the same interface as `CrewAIManager`:
   - `create_agent()`
   - `start_agent()`
   - `stop_agent()`
   - `query_agent()`
3. Register the manager in backend
4. Update frontend forms if the framework requires extra config options

---

## 📊 Future Enhancements

- **Microservices split**: separate agent execution, monitoring, and billing services  
- **Event-driven architecture**: Kafka/RabbitMQ for scaling agent runs  
- **Vector DB integration**: for long-term agent memory (Weaviate, Pinecone)  
- **Multi-agent orchestration**: CrewAI-style collaboration workflows  

---

## 🖼️ Diagram (Conceptual)

```

```
      ┌───────────────┐
      │   Frontend    │
      │  (Playground) │
      └───────┬───────┘
              │
    HTTP REST │
              ▼
      ┌───────────────┐
      │    Backend    │
      │   (FastAPI)   │
      └───────┬───────┘
              │
```

┌──────────────┼───────────────┐
│              │               │
▼              ▼               ▼
Agent Manager   Database      Config/Logs
(CrewAI, etc.)  (SQLAlchemy)  (env, Docker)

```

---

## 🔒 Security

- API key authentication (optional)  
- CORS control  
- Logging with error tracking  
- Planned: role-based access for teams  

---

## 📦 Deployment

- **Docker Compose**: single container setup for backend + frontend + DB  
- **Env-based config** for production/staging/dev  
- Future: Kubernetes support for scaling  

---

This architecture ensures the **Agent Dashboard** stays modular, scalable, and ready for SaaS transformation.

