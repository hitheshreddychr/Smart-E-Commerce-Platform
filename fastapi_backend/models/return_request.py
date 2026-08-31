from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from database.connection import Base


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    reason = Column(
        String(255),
        nullable=False
    )

    comment = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )