# ConversationIQ

ConversationIQ is a real-time operating procedure gap detector for banking AI agents. It simulates realistic banking conversations, identifies failed or confusing procedure paths, clusters recurring failure patterns, computes OP health scores, and recommends fixes. The full stack runs locally with Docker Compose and works without an OpenAI API key through deterministic mock fallbacks.

## Architecture

```text
Simulator / Seed Scripts
        |
        v
FastAPI ingestion + analytics API
        |
        +--> PostgreSQL: conversations, OP health, clusters, recommendations
        |
        +--> Redis: update publication and embedding cache
        |
        v
WebSocket /ws/live
        |
        v
Next.js dashboard
```

## Quick Start

```bash
git clone <repo-url>
cd ConversationIQ
cp .env.example .env
docker compose up --build
```

In a new terminal:

```bash
python3 scripts/seed_database.py
python3 scripts/run_clustering.py
python3 scripts/generate_recommendations.py
open http://localhost:3000
```

The scripts default to `http://localhost:8000`. To point them at another backend:

```bash
API_URL=http://localhost:8000 python3 scripts/e2e_test.py
```

## Railway Deployment

Deploy this repository to Railway as an isolated monorepo with separate services for `backend` and `frontend`, plus Railway-managed PostgreSQL and Redis services.

1. Create PostgreSQL and Redis services in the same Railway project.
2. Create a backend service from this repo with root directory `/backend` and config file `/backend/railway.json`.
3. Create a frontend service from this repo with root directory `/frontend` and config file `/frontend/railway.json`.
4. Generate public domains for the backend and frontend services before setting cross-service URLs.

Railway injects `PORT`; both Dockerfiles are configured to listen on it in production. The backend healthcheck is `/health`; the frontend healthcheck is `/`.

### Required Production Variables

Backend service:

```bash
APP_ENV=production
OPENAI_API_KEY=<add manually in Railway>
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
CORS_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
EMBEDDING_MODE=mock
```

Frontend service:

```bash
NEXT_PUBLIC_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
NEXT_PUBLIC_WS_URL=wss://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

Use the actual Railway service names in reference variables if yours differ from `Postgres`, `Redis`, `backend`, or `frontend`. `OPENAI_API_KEY`, `DATABASE_URL`, and `REDIS_URL` are production secrets or secret-bearing references and should stay in Railway variables only. Do not commit real API keys or database URLs.

`NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL` are public frontend build-time variables. Set them before the first frontend deploy, and redeploy the frontend after changing either value.

## Run Tests

For local checks outside Docker, install backend and frontend dependencies first:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r backend/requirements.txt
cd frontend && npm ci && cd ..
```

```bash
# Main local check
scripts/check_project.sh

# Full local check, including Docker Compose E2E smoke test
scripts/check_project.sh --with-docker
```

Individual commands:

```bash
# Backend
cd backend && python3 -m pytest tests/ -v

# Frontend
cd frontend && npm test

# End-to-end
python3 scripts/e2e_test.py

# Docker smoke test
bash scripts/docker_smoke_test.sh
```

## Without OpenAI API Key

In development, the classifier and recommender fall back to rule-based mocks automatically when `OPENAI_API_KEY` is empty. All features work. Recommendations will say `Mock recommendation - add OPENAI_API_KEY for AI-generated suggestions.`

In production (`APP_ENV=production` or a Railway environment named `production`), the backend requires `OPENAI_API_KEY` on startup so production uses OpenAI instead of the local mock fallback.

## Embeddings

Docker defaults to `EMBEDDING_MODE=mock` for fast, deterministic local demos. Set `EMBEDDING_MODE=transformer` to use `sentence-transformers/all-MiniLM-L6-v2`.

## OP Health Score Formula

Each operating procedure is scored from 0 to 100:

```text
score =
  resolution_rate * 40
  + (1 - escalation_rate) * 25
  + (1 - loop_rate) * 20
  + (1 - min(avg_turns / 10, 1)) * 10
  + sentiment_score * 5
```

Thresholds:

- `>= 80`: healthy
- `60-79`: warning
- `< 60`: critical

## Demo Walkthrough

1. Start the stack with `docker compose up --build`.
2. Open `http://localhost:3000` and leave the dashboard visible.
3. Run `python3 scripts/seed_database.py` and watch the live feed update.
4. Run `python3 scripts/run_clustering.py` to populate failure pattern analysis.
5. Run `python3 scripts/generate_recommendations.py` to create fix recommendations.
6. Open a weak OP detail page, inspect trend, clusters, transcripts, and recommendations.
7. Run `python3 scripts/e2e_test.py` to prove the full pipeline.
