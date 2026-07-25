from pydantic import BaseModel, Field


class ImportSummary(BaseModel):
    customers_created: int = Field(ge=0)
    customers_updated: int = Field(ge=0)
    transactions_created: int = Field(ge=0)
    transactions_skipped: int = Field(ge=0)
    rows_processed: int = Field(ge=0)


class ImportResponse(BaseModel):
    status: str = Field(default="success")
    message: str
    data: ImportSummary
    request_id: str
