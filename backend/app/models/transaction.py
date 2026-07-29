from datetime import date, time

from sqlalchemy import Date, Float, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id", ondelete="CASCADE"), index=True, nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    transaction_time: Mapped[time] = mapped_column(Time, nullable=False)
    transaction_amount: Mapped[float] = mapped_column(Float, nullable=False)
    # These fields are part of the banking record, rather than UI-only labels.
    # They allow balances and all downstream intelligence to reason about cashflow.
    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False, default="legacy")
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    merchant: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")

    customer = relationship("Customer", back_populates="transactions")
    fraud_analyses = relationship("FraudAnalysis", back_populates="transaction", cascade="all, delete-orphan")
