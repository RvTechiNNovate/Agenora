FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Install system dependencies + uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential curl && \
    pip install --upgrade pip && \
    pip install uv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock* requirements.txt* ./

# Install dependencies with uv (faster than pip)
# 1. Prefer uv.lock if available (frozen versions)
# 2. Otherwise fallback to requirements.txt
RUN if [ -f "uv.lock" ]; then \
        uv sync --frozen --no-dev; \
    elif [ -f "requirements.txt" ]; then \
        uv add --system -r requirements.txt; \
    fi

# Create logs directory
RUN mkdir -p logs

# Copy application code
COPY . .

# Expose application port
EXPOSE 8000

# Create a non-root user
RUN addgroup --system app && \
    adduser --system --group app

RUN chown -R app:app /app

USER app

# Run the application with Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "300", "backend.api.app:app"]
