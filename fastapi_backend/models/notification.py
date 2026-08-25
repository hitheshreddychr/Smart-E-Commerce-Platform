from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from database.connection import Base


class Notification(Base):
    __tablename__ = "notifications"

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

    type = Column(
        String(100),
        nullable=False
    )

    message = Column(
        String(500),
        nullable=False
    )

    read_status = Column(
        Boolean,
        nullable=False,
        default=False
    )

    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )