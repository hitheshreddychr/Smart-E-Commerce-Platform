from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.notification import Notification
from schemas.notification import (
    NotificationReadRequest,
    NotificationResponse,
)
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# GET USER NOTIFICATIONS
# GET /notifications
# ============================================================

@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user["id"]
        )
        .order_by(
            Notification.timestamp.desc()
        )
        .all()
    )

    return notifications


# ============================================================
# MARK NOTIFICATIONS AS READ
# POST /notifications/read
# ============================================================

@router.post(
    "/read"
)
def mark_notifications_as_read(
    notification_data: NotificationReadRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.id.in_(
                notification_data.notification_ids
            ),
            Notification.user_id == current_user["id"]
        )
        .all()
    )

    if not notifications:
        raise HTTPException(
            status_code=404,
            detail="Notifications not found"
        )

    for notification in notifications:
        notification.read_status = True

    db.commit()

    return {
        "message": "Notifications marked as read"
    }