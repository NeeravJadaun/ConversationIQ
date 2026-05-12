from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class FailureClusterOut(BaseModel):
    id: int
    op_id: str
    cluster_label: int
    size: int
    centroid_summary: str
    example_conversation_ids: list[str]
    gap_description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationOut(BaseModel):
    id: int
    op_id: str
    cluster_id: int | None
    recommendation_text: str
    priority: Literal["high", "medium", "low"]
    status: Literal["open", "acknowledged", "resolved"]
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationCreate(BaseModel):
    op_id: str
    cluster_id: int | None = None


class RecommendationStatusUpdate(BaseModel):
    status: Literal["open", "acknowledged", "resolved"]
