from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class OperatingProcedure(Base):
    __tablename__ = "operating_procedures"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    health_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    resolution_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    escalation_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    loop_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_turn_count: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_sentiment_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    conversation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
