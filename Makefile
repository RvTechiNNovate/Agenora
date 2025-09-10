.PHONY: help setup install-deps install-python install-docker install-uv run clean docker docker-run docker-compose docker-stop

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make setup             - Full project setup (installs Python, Docker, uv, dependencies)"
	@echo "  make install-deps      - Install project dependencies (uv sync)"
	@echo "  make run               - Run the application"
	@echo "  make clean             - Clean up cache files"
	@echo "  make docker            - Build Docker image"
	@echo "  make docker-run        - Run Docker container"
	@echo "  make docker-compose    - Start services with docker compose"
	@echo "  make docker-stop       - Stop services with docker compose"

# 🔹 Setup everything
setup: install-python install-docker install-uv install-deps
	@echo "✅ Full setup complete!"

# 🔹 Install Python (Ubuntu example)
install-python:
	@echo "Installing Python 3.11..."
	@if ! command -v python3.11 >/dev/null 2>&1; then \
		sudo apt-get update && \
		sudo apt-get install -y software-properties-common && \
		sudo add-apt-repository -y ppa:deadsnakes/ppa && \
		sudo apt-get update && \
		sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils; \
	else \
		echo "Python 3.11 already installed"; \
	fi


# 🔹 Install Docker
install-docker:
	@echo "Installing Docker..."
	@if ! command -v docker >/dev/null 2>&1; then \
		curl -fsSL https://get.docker.com | sh; \
	else \
		echo "Docker already installed"; \
	fi

# 🔹 Install uv
install-uv:
	@echo "Installing uv..."
	@if ! command -v uv >/dev/null 2>&1; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		export PATH="$$HOME/.cargo/bin:$$PATH"; \
	else \
		echo "uv already installed"; \
	fi

# 🔹 Install project deps
install-deps:
	@echo "Installing project dependencies..."
	uv sync
	@echo "✅ Dependencies installed!"

# 🔹 Run app
run:
	uv run run.py

# 🔹 Clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov/ dist/ build/

# 🔹 Docker commands
docker:
	docker build -t agent-dashboard .

docker-run:
	docker run -p 8000:8000 --env-file backend/.env agent-dashboard

docker-compose:
	docker compose up -d

docker-stop:
	docker compose down
