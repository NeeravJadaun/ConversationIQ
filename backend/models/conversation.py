from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


jsonb_type = JSON().with_variant(JSONB, "postgresql")
embedding_type = JSON().with_variant(ARRAY(Float), "postgresql")


class ResolutionStatus(str, Enum):
    resolved = "resolved"
    escalated = "escalated"
    looped = "looped"
    failed = "failed"


class CustomerSentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    op_id: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    op_name: Mapped[str] = mapped_column(String(100), nullable=False)
    turns: Mapped[list[dict]] = mapped_column(jsonb_type, nullable=False)
    resolution_status: Mapped[ResolutionStatus] = mapped_column(SAEnum(ResolutionStatus), index=True, nullable=False)
    turn_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_sentiment: Mapped[CustomerSentiment] = mapped_column(SAEnum(CustomerSentiment), nullable=False)
    intent_detected: Mapped[str] = mapped_column(Text, nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_intent_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(embedding_type, nullable=True)
    cluster_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    session_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
