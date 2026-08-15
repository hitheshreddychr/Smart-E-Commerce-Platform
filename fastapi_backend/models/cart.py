from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from database.connection import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        default=1,
        nullable=False
    )

    product = relationship("Product")