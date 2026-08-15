from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    stock: int = 0
    images: str | None = None
    category: str = "General"
    popularity: int = 0


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    images: str | None = None
    category: str | None = None
    popularity: int | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    images: str | None
    category: str
    popularity: int

    model_config = ConfigDict(from_attributes=True)