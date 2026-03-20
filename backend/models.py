from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_name: Mapped[str] = mapped_column(String(100), index=True)
    preferred_language: Mapped[str] = mapped_column(String(50), index=True)
    problem_name: Mapped[str] = mapped_column(String(120), index=True)
    code_submission: Mapped[str] = mapped_column(Text)
    mistake_type: Mapped[str] = mapped_column(String(50), index=True)
    confidence: Mapped[str] = mapped_column(String(20), default="medium", index=True)
    generated_feedback: Mapped[str] = mapped_column(Text)
    repeated_pattern_notes: Mapped[str] = mapped_column(Text)
    recommendation_notes: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
