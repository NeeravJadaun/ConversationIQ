from datetime import datetime

from pydantic import BaseModel

from schemas.conversation import ConversationOut


class OperatingProcedureOut(BaseModel):
    id: str
    name: str
    description: str
    health_score: float
    resolution_rate: float
    escalation_rate: float
    loop_rate: float
    avg_turn_count: float
    avg_sentiment_score: float
    conversation_count: int
    last_computed_at: datetime

    model_config = {"from_attributes": True}


class ProcedureDetail(OperatingProcedureOut):
    recent_conversations: list[ConversationOut]
    failure_clusters: list[dict]
    recommendations: list[dict]
    breakdown: dict[str, float]


class TrendPoint(BaseModel):
    date: str
    health_score: float
    resolved: int
    escalated: int
    looped: int
    failed: int
