from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from database.connection import Base


class Review(Base):
    __tablename__ = "reviews"

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

    rating = Column(
        Integer,
        nullable=False
    )

    comment = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="approved"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )