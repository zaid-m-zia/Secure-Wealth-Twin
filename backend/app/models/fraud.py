from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class FraudAnalysis(TimestampMixin, Base):
    __tablename__ = "fraud_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id", ondelete="CASCADE"), index=True, nullable=False)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.transaction_id", ondelete="CASCADE"), index=True, nullable=False)
    fraud_score_placeholder: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    anomaly_reason_placeholder: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation_placeholder: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    customer = relationship("Customer", back_populates="fraud_analyses")
    transaction = relationship("Transaction", back_populates="fraud_analyses")
