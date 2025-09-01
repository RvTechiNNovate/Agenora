# Configuration Options

This document describes the configuration options available in Agenora.

## Configuration Structure

Agenora uses a modular configuration system organized into logical sections:

```python
config
├── database     # Database settings
├── api          # API server settings
├── logging      # Logging configuration
├── performance  # Performance tuning
├── security     # Security settings
└── llm          # Language model settings
```

## Environment Variables

All configuration options can be set using environment variables. We recommend using a `.env` file in development and proper environment variable management in production.

## Database Configuration

| Option | Environment Variable | Description | Default |
|--------|---------------------|-------------|---------|
| `url` | `DATABASE_URL` | Database connection URL | `sqlite:///./Agenora.db` |
| `connect_args` | - | Additional connection arguments | `{"check_same_thread": False}` (for SQLite) |
| `pool_size` | `DB_POOL_SIZE` | Connection pool size | `5` |
| `max_overflow` | `DB_MAX_OVERFLOW` | Maximum overflow connections | `10` |

## API Configuration

| Option | Environment Variable | Description | Default |
|--------|---------------------|-------------|---------|
| `host` | `API_HOST` | Host to bind the API server | `0.0.0.0` |
| `port` | `API_PORT` | Port to bind the API server | `8000` |
| `debug` | `DEBUG` | Enable debug mode | `False` |
| `cors_origins` | `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000,http://localhost:8000` |

## Logging Configuration

| Option | Environment Variable | Description | Default |
|--------|---------------------|-------------|---------|
| `level` | `LOG_LEVEL` | Logging level | `INFO` |
| `format` | `LOG_FORMAT` | Log message format | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` |
| `file` | `LOG_FILE` | Log file path | `None` (console only) |

## Performance Configuration

| Option | Environment Variable | Description | Default |
|--------|---------------------|-------------|---------|
| `max_workers` | `MAX_WORKERS` | Maximum number of worker threads | `4` |
| `worker_timeout` | `WORKER_TIMEOUT` | Worker timeout in seconds | `60` |
| `cache_enabled` | `CACHE_ENABLED` | Enable response caching | `True` |
| `cache_ttl` | `CACHE_TTL` | Cache time-to-live in seconds | `3600` |

## Security Configuration

| Option | Environment Variable | Description | Default |
|--------|---------------------|-------------|---------|
| `secret_key` | `SECRET_KEY` | Secret key for session encryption | `supersecretkey` (change in production!) |
| `token_expire_minutes` | `TOKEN_EXPIRE_MINUTES` | Token expiration time in minutes | `30` |
| `allowed_hosts` | `ALLOWED_HOSTS` | Allowed hosts (comma-separated) | `localhost,127.0.0.1` |

## LLM Configuration

| Option | Environment Variable | Description | Default |
|--------|---------------------|-------------|---------|
| `default_provider` | `DEFAULT_LLM_PROVIDER` | Default LLM provider | `openai` |
| `default_model` | `DEFAULT_LLM_MODEL` | Default model name | `gpt-3.5-turbo` |
| `openai_api_key` | `OPENAI_API_KEY` | OpenAI API key | - |
| `anthropic_api_key` | `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `azure_api_key` | `AZURE_API_KEY` | Azure OpenAI API key | - |
| `azure_endpoint` | `AZURE_ENDPOINT` | Azure OpenAI endpoint | - |

## Example Configuration

Here's an example `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/agenora

# API Server
API_PORT=8080
DEBUG=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/agenora.log

# LLM Providers
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Security
SECRET_KEY=your-secure-secret-key
```

## Configuration Files

The configuration system is implemented in the following files:

- `backend/core/config/__init__.py`: Main configuration container
- `backend/core/config/database_config.py`: Database configuration
- `backend/core/config/api_config.py`: API server configuration
- `backend/core/config/logging_config.py`: Logging configuration
- `backend/core/config/performance_config.py`: Performance configuration
- `backend/core/config/security_config.py`: Security configuration
- `backend/core/config/llm_config.py`: LLM provider configuration
