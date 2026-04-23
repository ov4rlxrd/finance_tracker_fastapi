from typing import Annotated

from app.api.dependencies.auth import CurrentUser
from app.exceptions.user import AccountNotVerified
from app.models.models import User
from fastapi import  Depends



async def get_verified_user(current_user:CurrentUser) -> User:

    if not current_user.is_verified:
        raise AccountNotVerified()
    return current_user

VerifiedUser = Annotated[User, Depends(get_verified_user)]