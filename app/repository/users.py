from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import delete as sql_delete
from app.core.security import hash_password
from app.models.models import User, Wallet, PasswordResetToken
from app.schemas.schemas import UserCreate, UserUpdate


class UserRepository:
    @classmethod
    async def add_user(cls, data: UserCreate, session: AsyncSession) -> User | None:
        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            email = data.email.lower()
        )
        session.add(user)
        await session.flush()
        wallet = Wallet(
            user_id=user.id,
            name=data.initial_wallet_name,
            balance=data.initial_wallet_balance,
        )

        session.add(wallet)
        await session.commit()
        await session.refresh(user)
        stmt = (
            select(User)
            .options(selectinload(User.wallets))
            .where(User.id == user.id)
        )
        result = await session.execute(stmt)
        return result.scalars().one()

    @classmethod
    async def find_by_id(cls, user_id: int, session: AsyncSession):
        query = (select(User)
                 .where(User.id == user_id,
                                   User.is_active.is_(True),
                                    User.deleted_at.is_(None),
                                   )
                 )

        result = await session.execute(query)
        user = result.scalars().first()
        return user

    @classmethod
    async def delete_user(cls, user_id:int, session: AsyncSession):
        user = await session.scalar(
            select(User).where(User.id == user_id,
                               User.is_active.is_(True),
                               User.deleted_at.is_(None),
            )
        )
        if user is None:
            return None
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(user)
        return True

    @classmethod
    async def update_user(cls, user_id: int, data: UserUpdate, session: AsyncSession):
        user = await session.get(User, user_id)
        if user is None:
            return None
        user.username = data.username
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def create_reset_token(cls, user_id:int, token_hash:str, expires_at:datetime, session: AsyncSession)-> PasswordResetToken | None:
        reset_token = PasswordResetToken(user_id=user_id,token_hash=token_hash,expires_at=expires_at)
        session.add(reset_token)
        await session.commit()
        await session.refresh(reset_token)
        return reset_token

    @classmethod
    async def delete_reset_token(cls, reset_token:PasswordResetToken, session: AsyncSession):
        await session.delete(reset_token)
        await session.commit()

    @classmethod
    async def delete_reset_tokens_for_user(cls, user_id:int, session: AsyncSession):
        user = await UserRepository.find_by_id(user_id, session)
        if user:
            await session.execute(
                sql_delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
            )
        else:
            return None



class AuthRepository:
    @classmethod
    async def get_by_email(cls, email: str, session: AsyncSession):
        result = await session.execute(
            select(User).where(func.lower(User.email) == email.lower(),
                               User.is_active.is_(True),
                               User.deleted_at.is_(None),
                               )
        )
        return result.scalars().first()

    @classmethod
    async def get_by_username(cls, username: str, session: AsyncSession):
        result = await session.execute(
            select(User).where(func.lower(User.username) == username.lower(),
                               User.is_active.is_(True),
                               User.deleted_at.is_(None),)

        )
        return result.scalars().first()

    @classmethod
    async def get_reset_token_by_hash_token(cls, token_hash: str, session: AsyncSession):
        result = await session.execute(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        )
        return result.scalars().first()
class AdminRepository:
    @classmethod
    async def find_by_id_admin(cls, user_id: int, session: AsyncSession):
        query = (select(User)
                 .where(User.id == user_id,
                                   )
                 )

        result = await session.execute(query)
        user = result.scalars().first()
        return user