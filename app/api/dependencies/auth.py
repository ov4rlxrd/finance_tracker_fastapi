from typing import Annotated

from app.exceptions.user import InvalidToken, UserNotFound, UserIsDisabled
from fastapi import Depends, HTTPException

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
        raise InvalidToken()
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise InvalidToken()
    user = await UserRepository.find_by_id(user_id_int, session)
    if not user:
        raise UserNotFound()
    if not user.is_active or user.deleted_at is not None:
        raise UserIsDisabled()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
