from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CartCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartUpdate(BaseModel):
    product_id: int
    quantity: int


class CartRemove(BaseModel):
    product_id: int


class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    product_name: str
    price: Decimal
    quantity: int
    item_total: Decimal
    stock: int

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    cart_total: Decimal
    tax: Decimal
    grand_total: Decimal