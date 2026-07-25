from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"

    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id", ondelete="CASCADE"), primary_key=True)
    avg_transaction_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transaction_frequency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    spending_pattern_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    risk_flags_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="behavior_profile")
