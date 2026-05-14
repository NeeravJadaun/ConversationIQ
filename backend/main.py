from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models  # noqa: F401
from api.routes import clusters_router, conversations_router, procedures_router, recommendations_router, websocket_router
from core.config import Settings, get_settings
from core.database import create_all_tables
from core.database import SessionLocal
from services.health_scorer import ensure_operating_procedures


def _initialize_app(settings: Settings) -> None:
    if settings.is_production and settings.normalized_openai_api_key is None:
        raise RuntimeError("OPENAI_API_KEY is required in production.")
    last_error: Exception | None = None
    for _ in range(10):
        try:
            create_all_tables()
            last_error = None
            break
        except Exception as exc:
            last_error = exc
            time.sleep(2)
    if last_error is not None:
        raise last_error
    db = SessionLocal()
    try:
        ensure_operating_procedures(db)
    finally:
        db.close()


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        _initialize_app(settings)
        yield

    app = FastAPI(title="ConversationIQ", version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(conversations_router)
    app.include_router(procedures_router)
    app.include_router(clusters_router)
    app.include_router(recommendations_router)
    app.include_router(websocket_router)
    return app


app = create_app()
