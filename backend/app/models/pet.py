from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    species: Mapped[str] = mapped_column(String(80), nullable=False)
    morph: Mapped[str | None] = mapped_column(String(120))
    birth_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    weight: Mapped[float | None] = mapped_column(Float)
    length: Mapped[float | None] = mapped_column(Float)
    feeding_cycle: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    last_feeding_date: Mapped[date | None] = mapped_column(Date)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="pets")
    growth_records = relationship(
        "GrowthRecord",
        back_populates="pet",
        cascade="all, delete-orphan",
        order_by="GrowthRecord.date",
    )
    feeding_records = relationship(
        "FeedingRecord",
        back_populates="pet",
        cascade="all, delete-orphan",
        order_by="FeedingRecord.date",
    )
    reminders = relationship(
        "Reminder",
        back_populates="pet",
        cascade="all, delete-orphan",
        order_by="Reminder.due_date",
    )
