#this controls access based on user roles

from fastapi import HTTPException


def require_role(*allowed_roles):
    def check_role(current_user):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user

    return check_role