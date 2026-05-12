from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from models import Conversation, FailureCluster, OperatingProcedure, Recommendation
from schemas.procedure import OperatingProcedureOut, ProcedureDetail, TrendPoint
from services.health_scorer import compute_all_health_scores, ensure_operating_procedures

router = APIRouter(prefix="/api/procedures", tags=["procedures"])


def _as_dict(row) -> dict:
    data = row.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


@router.get("", response_model=list[OperatingProcedureOut])
def list_procedures(db: Session = Depends(get_db)):
    ensure_operating_procedures(db)
    compute_all_health_scores(db)
    return db.query(OperatingProcedure).order_by(OperatingProcedure.id).all()


@router.get("/{op_id}", response_model=ProcedureDetail)
def get_procedure(op_id: str, db: Session = Depends(get_db)):
    ensure_operating_procedures(db)
    op = db.get(OperatingProcedure, op_id)
    if op is None:
        raise HTTPException(status_code=404, detail="Operating procedure not found")
    recent = db.query(Conversation).filter(Conversation.op_id == op_id).order_by(Conversation.created_at.desc()).limit(20).all()
    clusters = db.query(FailureCluster).filter(FailureCluster.op_id == op_id).order_by(FailureCluster.size.desc()).all()
    recommendations = db.query(Recommendation).filter(Recommendation.op_id == op_id).order_by(Recommendation.created_at.desc()).all()
    return {
        **_as_dict(op),
        "recent_conversations": recent,
        "failure_clusters": [_as_dict(row) for row in clusters],
        "recommendations": [_as_dict(row) for row in recommendations],
        "breakdown": {
            "resolution_rate": op.resolution_rate,
            "escalation_rate": op.escalation_rate,
            "loop_rate": op.loop_rate,
            "avg_turn_count": op.avg_turn_count,
            "avg_sentiment_score": op.avg_sentiment_score,
        },
    }


@router.get("/{op_id}/trend", response_model=list[TrendPoint])
def get_trend(op_id: str, db: Session = Depends(get_db)):
    op = db.get(OperatingProcedure, op_id)
    if op is None:
        raise HTTPException(status_code=404, detail="Operating procedure not found")
    today = datetime.now(timezone.utc).date()
    points = []
    base = op.health_score or 70
    for index in range(30):
        day = today - timedelta(days=29 - index)
        wave = ((index % 7) - 3) * 1.2
        score = max(25, min(98, base + wave - (29 - index) * 0.12))
        points.append(
            TrendPoint(
                date=day.isoformat(),
                health_score=round(score, 1),
                resolved=max(0, int(op.resolution_rate * 20)),
                escalated=max(0, int(op.escalation_rate * 20)),
                looped=max(0, int(op.loop_rate * 20)),
                failed=max(0, 20 - int(op.resolution_rate * 20)),
            )
        )
    return points
