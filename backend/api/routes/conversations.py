from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from api.deps import get_db
from api.routes.websocket import broadcast_update
from core.redis_client import publish
from models import Conversation, OperatingProcedure
from schemas.conversation import BatchIngestResponse, ConversationCreate, ConversationOut
from services.classifier import classify_conversation
from services.embedder import embed_conversation
from services.health_scorer import compute_health_score, ensure_operating_procedures

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _payload_to_dict(payload: ConversationCreate) -> dict:
    data = payload.model_dump()
    data["turns"] = [turn.model_dump() if hasattr(turn, "model_dump") else turn for turn in payload.turns]
    return data


def save_conversation(payload: ConversationCreate, db: Session) -> Conversation:
    ensure_operating_procedures(db)
    data = _payload_to_dict(payload)
    conversation_id = data.get("conversation_id") or data.get("id")
    classification = classify_conversation(data)
    embedding = embed_conversation(data)
    row = Conversation(
        id=conversation_id,
        op_id=data["op_id"],
        op_name=data["op_name"],
        turns=data["turns"],
        resolution_status=data["resolution_status"],
        turn_count=data["turn_count"],
        customer_sentiment=data["customer_sentiment"],
        intent_detected=classification.get("intent_detected") or data["intent_detected"],
        failure_reason=classification.get("failure_reason"),
        suggested_intent_label=classification.get("suggested_intent_label"),
        embedding=embedding,
        session_duration_seconds=data["session_duration_seconds"],
        created_at=data.get("timestamp") or datetime.now(timezone.utc),
    )
    row = db.merge(row)
    db.commit()
    db.refresh(row)
    compute_health_score(row.op_id, db)
    return row


@router.post("/ingest", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def ingest_conversation(payload: ConversationCreate, db: Session = Depends(get_db)):
    row = save_conversation(payload, db)
    message = {
        "type": "new_conversation",
        "op_id": row.op_id,
        "op_name": row.op_name,
        "health_score": db.get(OperatingProcedure, row.op_id).health_score,
        "resolution_status": row.resolution_status,
        "intent_detected": row.intent_detected,
        "turn_count": row.turn_count,
        "timestamp": row.created_at.isoformat(),
    }
    publish("op_updates", message)
    await broadcast_update(message)
    return row


@router.post("/ingest/batch", response_model=BatchIngestResponse)
async def ingest_batch(payload: list[ConversationCreate], db: Session = Depends(get_db)):
    rows = [save_conversation(item, db) for item in payload]
    counts = Counter(row.resolution_status.value if hasattr(row.resolution_status, "value") else row.resolution_status for row in rows)
    affected_ops = sorted({row.op_id for row in rows})
    for op_id in affected_ops:
        await broadcast_update({"type": "health_update", "op_id": op_id, "timestamp": datetime.now(timezone.utc).isoformat()})
    return BatchIngestResponse(inserted=len(rows), by_status=dict(counts), affected_ops=affected_ops)


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    op_id: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Conversation)
    if op_id:
        query = query.filter(Conversation.op_id == op_id)
    if status_filter:
        query = query.filter(Conversation.resolution_status == status_filter)
    return query.order_by(Conversation.created_at.desc()).limit(limit).all()
