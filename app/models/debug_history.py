
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from app.database import Base


class DebugHistory(Base):
    __tablename__ = "debug_history"

    id = Column(Integer, primary_key=True, index=True)

    error_message = Column(Text, nullable=False)

    exception_type = Column(String(100), nullable=True)

    root_cause = Column(String(255), nullable=False)

    confidence = Column(String(50), nullable=True)

    fix_recommendation = Column(JSON, nullable=True)

    fix_validation = Column(JSON, nullable=True)

    ai_analysis = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
