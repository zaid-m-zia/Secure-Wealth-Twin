from datetime import date
from typing import Optional

from sqlalchemy import Date, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    account_balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    behavior_profile = relationship("BehaviorProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    digital_wealth_twin = relationship("DigitalWealthTwin", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    fraud_analyses = relationship("FraudAnalysis", back_populates="customer", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="customer", cascade="all, delete-orphan")
    agent_memory = relationship("AgentMemory", back_populates="customer", uselist=False, cascade="all, delete-orphan")
