import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from jose import JWTError, jwt

from database.connection import SessionLocal
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse
from utils.security import (
    SECRET_KEY,
    ALGORITHM,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# DATABASE
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# AUTH0 CONFIGURATION
# ============================================================

AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

if not AUTH0_CLIENT_ID:
    raise RuntimeError("AUTH0_CLIENT_ID is missing from .env")

if not AUTH0_CLIENT_SECRET:
    raise RuntimeError("AUTH0_CLIENT_SECRET is missing from .env")


oauth = OAuth()

oauth.register(
    name="auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    server_metadata_url=(
        "https://dev-36qvxsvdqvoe7yva.jp.auth0.com/"
        ".well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid profile email"
    }
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(
        user.password
    )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role="customer"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        existing_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "sub": str(existing_user.id),
            "email": existing_user.email,
            "role": existing_user.role,
            "type": "access"
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": str(existing_user.id),
            "email": existing_user.email,
            "role": existing_user.role,
            "type": "refresh"
        }
    )

    return {
        "message": "Login successful",
        "user": {
            "id": existing_user.id,
            "name": existing_user.name,
            "email": existing_user.email,
            "role": existing_user.role
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post("/refresh")
def refresh_token(
    refresh_token: str
):

    try:

        payload = verify_refresh_token(
            refresh_token
        )

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")

        if not user_id or not email or not role:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        new_access_token = create_access_token(
            {
                "sub": str(user_id),
                "email": email,
                "role": role,
                "type": "access"
            }
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )


# ============================================================
# CURRENT USER
# ============================================================

@router.get("/me")
def get_me(
    request: Request,
    db: Session = Depends(get_db)
):

    authorization = request.headers.get(
        "Authorization"
    )

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    try:

        scheme, token = authorization.split(" ")

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid access token"
            )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# ============================================================
# GOOGLE LOGIN
# ============================================================

@router.get("/login/google")
async def google_login(
    request: Request
):

    redirect_uri = request.url_for(
        "auth0_callback"
    )

    return await oauth.auth0.authorize_redirect(
        request,
        redirect_uri,
        connection="google-oauth2"
    )


# ============================================================
# FACEBOOK LOGIN
# ============================================================

@router.get("/login/facebook")
async def facebook_login(
    request: Request
):

    redirect_uri = request.url_for(
        "auth0_callback"
    )

    return await oauth.auth0.authorize_redirect(
        request,
        redirect_uri,
        connection="facebook"
    )


# ============================================================
# AUTH0 CALLBACK
# ============================================================

@router.get(
    "/callback",
    name="auth0_callback"
)
async def auth0_callback(
    request: Request,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # GET AUTH0 TOKEN
    # --------------------------------------------------------

    token = await oauth.auth0.authorize_access_token(
        request
    )

    # --------------------------------------------------------
    # GET USER INFORMATION
    # --------------------------------------------------------

    userinfo = token.get("userinfo")

    if not userinfo:

        userinfo = await oauth.auth0.userinfo(
            token["access_token"]
        )

    # --------------------------------------------------------
    # AUTH0 USER ID
    # --------------------------------------------------------

    auth0_id = userinfo.get("sub")

    if not auth0_id:
        raise HTTPException(
            status_code=400,
            detail="User ID not provided by Auth0"
        )

    # --------------------------------------------------------
    # USER NAME
    # --------------------------------------------------------

    name = (
        userinfo.get("name")
        or userinfo.get("nickname")
        or userinfo.get("given_name")
        or "Social User"
    )

    # --------------------------------------------------------
    # USER EMAIL
    # --------------------------------------------------------

    email = userinfo.get("email")

    # --------------------------------------------------------
    # FACEBOOK MAY NOT RETURN EMAIL
    # --------------------------------------------------------

    if not email:

        if auth0_id.startswith("facebook|"):

            safe_id = (
                auth0_id
                .replace("|", "_")
                .replace("/", "_")
                .replace(":", "_")
            )

            email = (
                f"facebook_{safe_id}"
                "@social.local"
            )

        elif auth0_id.startswith(
            "google-oauth2|"
        ):

            safe_id = (
                auth0_id
                .replace("|", "_")
                .replace("/", "_")
                .replace(":", "_")
            )

            email = (
                f"google_{safe_id}"
                "@social.local"
            )

        else:

            safe_id = (
                auth0_id
                .replace("|", "_")
                .replace("/", "_")
                .replace(":", "_")
            )

            email = (
                f"social_{safe_id}"
                "@social.local"
            )

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    if not user:

        user = User(
            name=name,
            email=email,
            password="AUTH0_SOCIAL_LOGIN",
            role="customer"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    # --------------------------------------------------------
    # CREATE ACCESS TOKEN
    # --------------------------------------------------------

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "type": "access"
        }
    )

    # --------------------------------------------------------
    # CREATE REFRESH TOKEN
    # --------------------------------------------------------

    refresh_token = create_refresh_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "type": "refresh"
        }
    )

    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    return {
        "message": "Auth0 login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }