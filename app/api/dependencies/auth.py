from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from app.core.security import verify_access_token, oauth2_scheme
from app.database import SessionDep
from app.models.models import User
from app.repository.users import UserRepository


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: SessionDep
) -> User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await UserRepository.find_by_id(user_id_int, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is disabled")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
