# This handles password hashing and JWT token creation and verification

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError


SECRET_KEY = "smart-ecommerce-secret-key"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# -----------------------------------------
# Password Hashing
# -----------------------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# -----------------------------------------
# Access Token
# -----------------------------------------

def create_access_token(data: dict) -> str:
    token_data = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token_data.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# -----------------------------------------
# Refresh Token
# -----------------------------------------

def create_refresh_token(data: dict) -> str:
    token_data = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    token_data.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# -----------------------------------------
# Decode and Verify Refresh Token
# -----------------------------------------

def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            return None

        if not payload.get("sub"):
            return None

        return payload

    except JWTError:
        return None