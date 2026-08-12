# This defines the Order request and response schemas

from decimal import Decimal

from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: Decimal

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True