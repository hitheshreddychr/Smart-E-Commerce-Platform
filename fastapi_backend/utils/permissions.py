from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from utils.security import ALGORITHM, SECRET_KEY


# ============================================================
# SECURITY
# ============================================================

security = HTTPBearer()


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    try:

        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        token_type = payload.get("type")

        if token_type != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid access token"
            )

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")

        if not user_id or not email or not role:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {
            "id": int(user_id),
            "email": email,
            "role": role
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# ============================================================
# ROLE BASED ACCESS
# ============================================================

def require_role(*allowed_roles):

    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):

        if current_user["role"] not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker


# ============================================================
# ADMIN ONLY
# ============================================================

def admin_required(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


# ============================================================
# STAFF ONLY
# ============================================================

def staff_required(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "staff":

        raise HTTPException(
            status_code=403,
            detail="Staff access required"
        )

    return current_user


# ============================================================
# CUSTOMER ONLY
# ============================================================

def customer_required(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "customer":

        raise HTTPException(
            status_code=403,
            detail="Customer access required"
        )

    return current_user


# ============================================================
# ADMIN OR STAFF
# ============================================================

def admin_or_staff_required(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] not in ["admin", "staff"]:

        raise HTTPException(
            status_code=403,
            detail="Admin or Staff access required"
        )

    return current_user


# ============================================================
# AUTHENTICATED USER
# ============================================================

def authenticated_required(
    current_user: dict = Depends(get_current_user)
):

    return current_user


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

require_admin = admin_required

require_staff = staff_required

require_customer = customer_required

require_admin_or_staff = admin_or_staff_required