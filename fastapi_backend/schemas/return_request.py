from datetime import datetime

from pydantic import BaseModel


class ReturnRequestCreate(BaseModel):
    reason: str
    comment: str | None = None


class ReturnRequestResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    reason: str
    comment: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True