from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ResolutionStatus = Literal["resolved", "escalated", "looped", "failed"]
CustomerSentiment = Literal["positive", "neutral", "negative"]


class Turn(BaseModel):
    role: Literal["customer", "agent"]
    text: str
    timestamp: str


class ConversationBase(BaseModel):
    conversation_id: str | None = None
    id: str | None = None
    op_id: str
    op_name: str
    turns: list[Turn]
    resolution_status: ResolutionStatus
    turn_count: int
    customer_sentiment: CustomerSentiment
    intent_detected: str
    timestamp: datetime | None = None
    session_duration_seconds: int


class ConversationCreate(ConversationBase):
    pass


class ConversationOut(BaseModel):
    id: str
    op_id: str
    op_name: str
    turns: list[dict]
    resolution_status: ResolutionStatus
    turn_count: int
    customer_sentiment: CustomerSentiment
    intent_detected: str
    failure_reason: str | None = None
    suggested_intent_label: str | None = None
    cluster_id: int | None = None
    session_duration_seconds: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchIngestResponse(BaseModel):
    inserted: int
    by_status: dict[str, int]
    affected_ops: list[str]


class ConversationFilters(BaseModel):
    op_id: str | None = None
    status: ResolutionStatus | None = None
    limit: int = Field(default=50, le=200)
