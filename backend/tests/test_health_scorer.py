from datetime import datetime, timezone

from models import Conversation
from services.health_scorer import compute_health_score


def add_conversation(db, op_id="OP-01", status="resolved", sentiment="positive", turns=3, index=0):
    row = Conversation(
        id=f"{op_id}-{status}-{index}",
        op_id=op_id,
        op_name="Card Lock / Freeze",
        turns=[{"role": "customer", "text": "lock my card", "timestamp": "now"}],
        resolution_status=status,
        turn_count=turns,
        customer_sentiment=sentiment,
        intent_detected="lock my card",
        embedding=[0.1] * 384,
        session_duration_seconds=120,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()


def test_perfect_score(db):
    for i in range(100):
        add_conversation(db, index=i)
    assert compute_health_score("OP-01", db) >= 95


def test_critical_score(db):
    for i in range(80):
        add_conversation(db, status="failed", sentiment="negative", turns=8, index=i)
    for i in range(80, 100):
        add_conversation(db, status="escalated", sentiment="negative", turns=8, index=i)
    assert compute_health_score("OP-01", db) < 60


def test_score_components_weighted_correctly(db):
    for i in range(50):
        add_conversation(db, index=i)
    for i in range(50, 100):
        add_conversation(db, status="failed", sentiment="neutral", turns=4, index=i)
    score = compute_health_score("OP-01", db)
    assert 20 <= score <= 75


def test_score_updates_on_new_conversation(db):
    for i in range(10):
        add_conversation(db, index=i)
    before = compute_health_score("OP-01", db)
    add_conversation(db, status="failed", sentiment="negative", turns=9, index=99)
    after = compute_health_score("OP-01", db)
    assert after < before
