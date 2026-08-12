from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from models.user import User
from utils.security import hash_password

router = APIRouter(
    prefix="/auth/password",
    tags=["Password Management"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/forgot")
def request_password_reset(
    data: dict,
    db: Session = Depends(get_db)
):
    email = data.get("email")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email is required"
        )

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "Password reset request successful",
        "email": user.email
    }


@router.post("/reset")
def reset_password(
    data: dict,
    db: Session = Depends(get_db)
):
    email = data.get("email")
    new_password = data.get("new_password")

    if not email or not new_password:
        raise HTTPException(
            status_code=400,
            detail="Email and new password are required"
        )

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.password = hash_password(new_password)

    db.commit()

    return {
        "message": "Password reset successful"
    }