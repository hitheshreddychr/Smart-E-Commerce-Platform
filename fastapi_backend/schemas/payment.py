from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CheckoutResponse(BaseModel):
    order_id: int
    amount: Decimal
    currency: str
    payment_status: str
    payment_intent_id: str
    payment_intent_client_secret: str | None
    checkout_session_id: str
    checkout_url: str | None


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_method: str
    transaction_id: str | None
    status: str
    timestamp: datetime

    model_config = ConfigDict(
        from_attributes=True
    )