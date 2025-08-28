
# Agent Dashboard 🚀

A **production-ready web dashboard** for creating, managing, and interacting with AI agents.  
Currently supports **CrewAI**, with plans to add **LangChain** and other frameworks in the future.

---

## ✨ Features

### 🔑 Agent Management
- Create agents with custom configurations  
- Define roles, tasks, and backstories  
- Choose language models and set parameters  
- Start, stop, and monitor agents  
- Version tracking and rollback capabilities
- Persistent storage with database support  

### 🧪 Interactive Playground
- Test agents in real-time via a chat interface  
- Send queries and view agent responses  
- Compare outputs across different LLM providers  

### ⚙️ Production-Ready
- Database persistence using **SQLAlchemy**  
- Comprehensive **logging system**  
- **API key authentication** for security  
- Robust **error handling and retries**  
- **Docker containerization** for easy deployment  
- Configurable environment settings  

---

## 🚀 Quick Start

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agent_dashboard.git
   cd agent_dashboard
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys and settings
   ```

5. Run the application:

   ```bash
   python run.py
   ```

6. Open [http://localhost:8000](http://localhost:8000) in your browser.

---

### Docker Deployment

1. Configure environment variables:

   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys and settings
   ```

2. Build and run with Docker Compose:

   ```bash
   docker-compose up -d
   ```

3. Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## ⚙️ Configuration

See [`backend/config.py`](backend/config.py) for all available settings.
Details on server, security, database, and performance parameters are listed in the [docs](docs/architecture.md#⚙️-configuration).

---

## 📖 API Documentation

* Swagger UI → [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
* ReDoc → [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

Key Endpoints:

* `GET /api/agents` – List all agents
* `POST /api/agent` – Create new agent
* `GET /api/agent/{id}` – Get agent details
* `POST /api/agent/{id}/start` – Start an agent
* `POST /api/agent/{id}/stop` – Stop an agent
* `POST /api/agent/{id}/query` – Query an agent
* `GET /api/health` – Health check

---

## 🏗️ Architecture

The system follows a **clean architecture pattern** with:

* **API Layer** (FastAPI routes)
* **Service Layer** (agent managers, e.g. CrewAIManager)
* **Data Layer** (SQLAlchemy ORM models)
* **Configuration Layer** (env-based config)
* **Frontend** (Playground UI)

👉 See [docs/architecture.md](docs/architecture.md) for full details and diagrams.

---

## ➕ Adding New Agent Frameworks

The system is modular:

1. Create a new manager class in `backend/agent_manager/`
2. Implement the same interface as `CrewAIManager`
3. Update the frontend if new config options are required

---

## 🤝 Contributing

We welcome contributions! 🎉

1. **Fork** the repo
2. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature
   ```
3. **Commit** your changes with clear messages
4. **Push** and open a **Pull Request**

✅ Please make sure to:

* Follow the project’s structure & style
* Add/update tests where relevant
* Update documentation for new features

---

## 🗺️ Roadmap / Next Steps

### Core Enhancements

* [ ] Agent versioning & snapshots
* [ ] Side-by-side model comparison
* [ ] Replay & debugging mode

### Monitoring & Analytics

* [ ] Token usage & cost tracking
* [ ] Analytics dashboard
* [ ] Crash/timeout alerting

### Collaboration

* [ ] Multi-user teams with RBAC
* [ ] Agent sharing & cloning

### Templates & Marketplace

* [ ] Prebuilt agent templates (FAQ bot, SQL agent, Summarizer)
* [ ] Community-driven marketplace

### Deployment & Integration

* [ ] Deploy agents as APIs
* [ ] Chat widget SDK for websites
* [ ] Webhooks & triggers

### Framework Support

* [ ] LangChain integration
* [ ] Support for Haystack, Autogen

### Business/SaaS Features

* [ ] Credit-based billing
* [ ] Subscription tiers
* [ ] Org-level dashboards

---

## 📜 License

MIT License – feel free to use and modify.

