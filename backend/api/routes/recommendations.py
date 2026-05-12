from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from models import Recommendation, RecommendationStatus
from schemas.cluster import RecommendationCreate, RecommendationOut, RecommendationStatusUpdate
from services.recommender import generate_recommendation

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationOut])
def list_recommendations(op_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Recommendation)
    if op_id:
        query = query.filter(Recommendation.op_id == op_id)
    return query.order_by(Recommendation.created_at.desc()).all()


@router.post("/generate", response_model=RecommendationOut)
def create_recommendation(payload: RecommendationCreate, db: Session = Depends(get_db)):
    try:
        return generate_recommendation(payload.op_id, payload.cluster_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{recommendation_id}", response_model=RecommendationOut)
def update_recommendation(recommendation_id: int, payload: RecommendationStatusUpdate, db: Session = Depends(get_db)):
    recommendation = db.get(Recommendation, recommendation_id)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    recommendation.status = RecommendationStatus(payload.status)
    db.commit()
    db.refresh(recommendation)
    return recommendation
