from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FeedingRecord(Base):
    __tablename__ = "feeding_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    pet_id: Mapped[str] = mapped_column(ForeignKey("pets.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    food_type: Mapped[str] = mapped_column(String(80), nullable=False)
    food_weight: Mapped[float | None] = mapped_column(Float)
    is_success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    refused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    pet = relationship("Pet", back_populates="feeding_records")
