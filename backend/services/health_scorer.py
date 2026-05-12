from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Conversation, OperatingProcedure, Recommendation, RecommendationStatus
from services.simulator import OPERATING_PROCEDURES


def _enum_value(value) -> str:
    return getattr(value, "value", value)


def ensure_operating_procedures(db: Session) -> None:
    for op_id, data in OPERATING_PROCEDURES.items():
        existing = db.get(OperatingProcedure, op_id)
        if existing is None:
            db.add(
                OperatingProcedure(
                    id=op_id,
                    name=data["name"],
                    description=data["description"],
                )
            )
    db.commit()


def compute_health_score(op_id: str, db: Session) -> float:
    op = db.get(OperatingProcedure, op_id)
    if op is None:
        data = OPERATING_PROCEDURES[op_id]
        op = OperatingProcedure(id=op_id, name=data["name"], description=data["description"])
        db.add(op)
        db.flush()

    conversations = db.query(Conversation).filter(Conversation.op_id == op_id).all()
    total = len(conversations)
    if total == 0:
        op.health_score = 0.0
        db.commit()
        return 0.0

    resolved = sum(1 for row in conversations if _enum_value(row.resolution_status) == "resolved")
    escalated = sum(1 for row in conversations if _enum_value(row.resolution_status) == "escalated")
    looped = sum(1 for row in conversations if _enum_value(row.resolution_status) == "looped")
    avg_turns = sum(row.turn_count for row in conversations) / total
    sentiment_score = sum({"positive": 1.0, "neutral": 0.5, "negative": 0.0}[_enum_value(row.customer_sentiment)] for row in conversations) / total
    resolution_rate = resolved / total
    escalation_rate = escalated / total
    loop_rate = looped / total
    score = (
        resolution_rate * 40
        + (1 - escalation_rate) * 25
        + (1 - loop_rate) * 20
        + (1 - min(avg_turns / 10, 1)) * 10
        + sentiment_score * 5
    )

    op.health_score = round(score, 2)
    op.resolution_rate = round(resolution_rate, 4)
    op.escalation_rate = round(escalation_rate, 4)
    op.loop_rate = round(loop_rate, 4)
    op.avg_turn_count = round(avg_turns, 2)
    op.avg_sentiment_score = round(sentiment_score, 4)
    op.conversation_count = total
    op.last_computed_at = datetime.now(timezone.utc)
    db.commit()
    return op.health_score


def compute_all_health_scores(db: Session) -> None:
    ensure_operating_procedures(db)
    op_ids = [row[0] for row in db.query(Conversation.op_id).group_by(Conversation.op_id).all()]
    for op_id in op_ids:
        compute_health_score(op_id, db)


def summary_stats(db: Session) -> dict:
    ensure_operating_procedures(db)
    ops = db.query(OperatingProcedure).all()
    conversations_today = db.query(func.count(Conversation.id)).scalar() or 0
    open_recommendations = db.query(func.count(Recommendation.id)).filter(Recommendation.status == RecommendationStatus.open).scalar() or 0
    avg = sum(op.health_score for op in ops) / len(ops) if ops else 0
    return {
        "total_ops": len(ops),
        "conversations_today": conversations_today,
        "avg_health_score": round(avg, 1),
        "open_recommendations": open_recommendations,
    }
