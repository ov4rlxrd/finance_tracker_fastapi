from typing import Annotated, List, Any

from fastapi import HTTPException, Depends
from starlette import status

from app.api.dependencies.auth import CurrentUser
from app.models.models import User
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    def __call__(self, current_user: CurrentUser) -> Any:
        if current_user.role in self.allowed_roles:
            return current_user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your not allowed to perform this action")

AdminUser = Annotated[User, Depends(RoleChecker(["admin"]))]