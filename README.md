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



##What should open

n8n UI: http://localhost:5678

FastAPI health: http://localhost:8000/health

FastAPI docs: http://localhost:8000/docs

##Expected checks
##1. API health
curl -s http://localhost:8000/health

Expected response:

{"ok":true}
##2. Postgres schema
set -a
source .env
set +a
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\dn"

Expected: schema app

##3. Postgres tables
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\dt app.*"

Expected tables:

agent_audit_log

events_inbox

events_results

##Services

postgres — database for the lab

n8n — workflow orchestrator

api — minimal FastAPI service with /health

##Notes

Real secrets must stay only in .env

.env.example contains placeholders only

Do not change N8N_ENCRYPTION_KEY after credentials are created in n8n
