from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    transaction_id: str = Field(min_length=1, max_length=64)
    customer_id: str = Field(min_length=1, max_length=64)
    transaction_date: date
    transaction_time: time
    transaction_amount: float = Field(ge=0)
    transaction_type: str = Field(default="legacy", max_length=32)
    category: str = Field(default="general", max_length=64)
    merchant: Optional[str] = Field(default=None, max_length=120)
    status: str = Field(default="completed", max_length=32)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    customer_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    transaction_date: Optional[date] = None
    transaction_time: Optional[time] = None
    transaction_amount: Optional[float] = Field(default=None, ge=0)
    transaction_type: Optional[str] = Field(default=None, max_length=32)
    category: Optional[str] = Field(default=None, max_length=64)
    merchant: Optional[str] = Field(default=None, max_length=120)
    status: Optional[str] = Field(default=None, max_length=32)


class TransactionRead(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime
