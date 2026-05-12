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
docker-compose up --build
```

In a new terminal:

```bash
python scripts/seed_database.py
python scripts/run_clustering.py
python scripts/generate_recommendations.py
open http://localhost:3000
```

## Run Tests

```bash
# Backend
docker-compose exec backend pytest tests/ -v

# Frontend
cd frontend && npm test

# End-to-end
python scripts/e2e_test.py
```

## Without OpenAI API Key

The classifier and recommender fall back to rule-based mocks automatically. All features work. Recommendations will say `Mock recommendation - add OPENAI_API_KEY for AI-generated suggestions.`

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

1. Start the stack with `docker-compose up --build`.
2. Open `http://localhost:3000` and leave the dashboard visible.
3. Run `python scripts/seed_database.py` and watch the live feed update.
4. Run `python scripts/run_clustering.py` to populate failure pattern analysis.
5. Run `python scripts/generate_recommendations.py` to create fix recommendations.
6. Open a weak OP detail page, inspect trend, clusters, transcripts, and recommendations.
7. Run `python scripts/e2e_test.py` to prove the full pipeline.
