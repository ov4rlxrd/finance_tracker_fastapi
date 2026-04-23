from datetime import datetime, timedelta, UTC, tzinfo

from app.core.security import generate_reset_token, hash_reset_token, hash_password, verify_password, \
    create_verify_token, verify_verify_token
from config import settings
from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user import UserAlreadyExists, EmailAlreadyExists, UserNotFound, ResetTokenException, \
    PasswordIncorrect
from app.repository.users import UserRepository, AuthRepository, AdminRepository
from app.schemas.schemas import UserCreate, UserResponse, UserUpdate, UserAdminResponse, ForgotPasswordEmailData, \
    VerifyRequest
from starlette import status


async def create_user(user: UserCreate, session: AsyncSession) -> UserResponse:
    if await AuthRepository.get_by_username(user.username, session):
        raise UserAlreadyExists()
    if await AuthRepository.get_by_email(user.email, session):
        raise EmailAlreadyExists()
    new_user = await UserRepository.add_user(user, session)
    return UserResponse.model_validate(new_user)


async def find_user(user_id: int, session: AsyncSession) -> UserAdminResponse:
    user = await AdminRepository.find_by_id_admin(user_id, session)
    if user is None:
        raise UserNotFound()
    return UserAdminResponse.model_validate(user)


async def delete_user_service(user_id: int, session: AsyncSession) -> None:
    return await UserRepository.delete_user(user_id, session)


async def update_user_service(user_update: UserUpdate, user_id: int, session: AsyncSession) -> UserResponse:
    return await UserRepository.update_user(user_id, user_update, session)

async def forgot_password_service(email: EmailStr, session: AsyncSession)-> ForgotPasswordEmailData | None:
    user = await AuthRepository.get_by_email(email, session)
    if user is None:
        return None
    await UserRepository.delete_reset_tokens_for_user(user.id, session)

    token = generate_reset_token()
    token_hash = hash_reset_token(token)
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.reset_token_expire_minutes)

    reset_token = await UserRepository.create_reset_token(user_id=user.id, token_hash=token_hash, expires_at=expires_at, session=session)
    return ForgotPasswordEmailData(to_email=user.email, username=user.username, token=token)


async def reset_password_service(token:str, new_password:str, session: AsyncSession):
    token_hash = hash_reset_token(token)
    reset_token = await AuthRepository.get_reset_token_by_hash_token(token_hash, session)
    if not reset_token:
        raise ResetTokenException()

    if reset_token.expires_at < datetime.now(UTC):
        await UserRepository.delete_reset_token(reset_token, session)
        raise ResetTokenException()

    user = await UserRepository.find_by_id(reset_token.user_id, session)

    if not user:
        raise ResetTokenException()
    user.password_hash = hash_password(new_password)

    await UserRepository.delete_reset_tokens_for_user(user.id, session)

    await session.commit()
    return True


async def change_password_service(current_password:str, new_password:str, user_id:int, session: AsyncSession):
    user = await UserRepository.find_by_id(user_id, session)
    if not user:
        raise UserNotFound()
    if not verify_password(current_password, user.password_hash):
        raise PasswordIncorrect()
    user.password_hash = hash_password(new_password)

    await UserRepository.delete_reset_tokens_for_user(user.id, session)
    await session.commit()
    return True

async def verify_user_service(email:str, session: AsyncSession):
    user = await AuthRepository.get_by_email(email, session)
    if not user:
        raise UserNotFound()
    token = create_verify_token(data={"sub": str(user.id)})

    return VerifyRequest(token=token, username=user.username, email=user.email)


async def verify_user_account_service(token:str, session: AsyncSession):
    user_id = verify_verify_token(token)
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
        raise UserNotFound()
    if user.is_verified:
        return {"message": "Account already verified"}
    user.is_verified = True
    await session.commit()
    return {"message": "User account is verified"}