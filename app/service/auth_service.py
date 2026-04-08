from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.security import verify_password, create_access_token
from app.exceptions.user import UserIsDisabled
from app.repository.users import AuthRepository
from app.schemas.schemas import Token
from config import settings


async def login_for_access_token_service(
        username:str,
        password:str,
        session: AsyncSession
):
    user = await AuthRepository.get_by_email(username, session)

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active or user.deleted_at is not None:
        raise UserIsDisabled()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


