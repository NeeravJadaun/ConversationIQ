from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from models.conversation import jsonb_type


class RecommendationPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class RecommendationStatus(str, Enum):
    open = "open"
    acknowledged = "acknowledged"
    resolved = "resolved"


class FailureCluster(Base):
    __tablename__ = "failure_clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    op_id: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    cluster_label: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    centroid_summary: Mapped[str] = mapped_column(Text, nullable=False)
    example_conversation_ids: Mapped[list[str]] = mapped_column(jsonb_type, nullable=False)
    gap_description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    op_id: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    cluster_id: Mapped[Optional[int]] = mapped_column(ForeignKey("failure_clusters.id"), nullable=True)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[RecommendationPriority] = mapped_column(SAEnum(RecommendationPriority), nullable=False)
    status: Mapped[RecommendationStatus] = mapped_column(
        SAEnum(RecommendationStatus),
        default=RecommendationStatus.open,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
