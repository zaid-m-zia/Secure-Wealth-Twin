from typing import Optional

from sqlalchemy import Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class DigitalWealthTwin(TimestampMixin, Base):
    __tablename__ = "digital_wealth_twins"

    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id", ondelete="CASCADE"), primary_key=True)
    financial_dna_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    wealth_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    health_score_placeholder: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    customer = relationship("Customer", back_populates="digital_wealth_twin")
