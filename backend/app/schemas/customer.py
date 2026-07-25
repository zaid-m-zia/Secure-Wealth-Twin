from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    customer_id: str = Field(min_length=1, max_length=64)
    dob: Optional[date] = None
    gender: Optional[str] = Field(default=None, max_length=16)
    location: Optional[str] = Field(default=None, max_length=120)
    account_balance: float = Field(default=0.0)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    dob: Optional[date] = None
    gender: Optional[str] = Field(default=None, max_length=16)
    location: Optional[str] = Field(default=None, max_length=120)
    account_balance: Optional[float] = None


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime
