# Deployment Guide

This document provides instructions for deploying Agenora in various environments.

## Local Deployment

### Prerequisites

- Python 3.10+
- Node.js 16+ (for the React frontend)
- Git

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/RvTechiNNovate/Agenora.git
   cd Agenora
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Access the application at http://localhost:8000

## Docker Deployment

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/RvTechiNNovate/Agenora.git
   cd Agenora
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. Build and start the Docker containers:
   ```bash
   docker-compose up -d
   ```

4. Access the application at http://localhost:8000

## Cloud Deployment

### AWS Elastic Beanstalk

1. Install the EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize your EB application:
   ```bash
   eb init -p python-3.10 agenora
   ```

3. Create an environment:
   ```bash
   eb create agenora-env
   ```

4. Deploy the application:
   ```bash
   eb deploy
   ```

### Google Cloud Run

1. Build the Docker image:
   ```bash
   docker build -t gcr.io/your-project/agenora .
   ```

2. Push the image to Google Container Registry:
   ```bash
   docker push gcr.io/your-project/agenora
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy agenora --image gcr.io/your-project/agenora --platform managed
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./Agenora.db` |
| `API_HOST` | Host to bind the API server | `0.0.0.0` |
| `API_PORT` | Port to bind the API server | `8000` |
| `DEBUG` | Enable debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `SECRET_KEY` | Secret key for session encryption | `supersecretkey` |

## Security Considerations

1. **API Keys**: Store API keys securely using environment variables, not in code.
2. **Database**: For production, use a proper database like PostgreSQL instead of SQLite.
3. **HTTPS**: Always use HTTPS in production environments.
4. **Authentication**: Implement proper authentication for production deployments.

## Monitoring

Monitor your Agenora deployment using:

- Application logs
- Database performance metrics
- API endpoint response times
- Resource utilization (CPU, memory)

## Scaling

For high-traffic deployments:

1. Use a production-grade database (PostgreSQL, MySQL)
2. Implement caching where appropriate
3. Consider using a load balancer for multiple instances
4. Monitor performance and scale resources as needed
