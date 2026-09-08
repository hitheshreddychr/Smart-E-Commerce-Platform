from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer

from database.connection import Base


class ProductView(Base):
    __tablename__ = "product_views"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    viewed_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )