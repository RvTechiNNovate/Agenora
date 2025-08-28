# Makefile for Agent Dashboard

.PHONY: run install test lint format clean docker docker-run docker-stop

run:
	python run.py

install:
	pip install -r requirements.txt

test:
	pytest -v tests/

lint:
	flake8 backend/ tests/
	isort --check backend/ tests/
	black --check backend/ tests/

format:
	isort backend/ tests/
	black backend/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ dist/ build/

docker:
	docker build -t agent-dashboard .

docker-run:
	docker run -p 8000:8000 --env-file backend/.env agent-dashboard

docker-compose:
	docker-compose up -d

docker-stop:
	docker-compose down
