from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    message: str
    read_status: bool
    timestamp: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class NotificationReadRequest(BaseModel):
    notification_ids: list[int]