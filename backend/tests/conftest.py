import os
import pathlib
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test_conversationiq.db"
os.environ["OPENAI_API_KEY"] = ""

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

import models  # noqa: F401,E402
from core.database import Base, SessionLocal, engine
from main import app
from services.health_scorer import ensure_operating_procedures


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    ensure_operating_procedures(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("api.routes.conversations.embed_conversation", lambda conversation: [0.1] * 384)
    return TestClient(app)
