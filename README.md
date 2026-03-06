# integration-automation-lab
n8n + Postgres + FastAPI lab for reliable automation patterns (idempotency, retries, DLQ, OAuth, LLM validation).

Local lab for learning reliable automation workflows with **n8n + Postgres + FastAPI**.

## Prerequisites

- Windows 11
- WSL2 (Ubuntu)
- Docker Desktop with WSL integration enabled
- Git

## Run in 5 minutes

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
