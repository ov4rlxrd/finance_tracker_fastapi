from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.exceptions.wallet import InsufficientFunds
from sqlalchemy import select, exists, Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import CurrencyEnum
from app.models.models import Wallet
from app.schemas.schemas import WalletCreate, WalletUpdate


class WalletRepository:
    @classmethod
    async def is_wallet_exist(cls, wallet_name: str, user_id:int, session: AsyncSession) -> bool:
        wallet = await cls._get_active_wallet(wallet_name, user_id, session)
        return wallet is not None

    @classmethod
    async def get_wallet_by_id(cls,wallet_id: int, user_id: int, session: AsyncSession) -> Wallet | None:
        return await session.scalar(select(Wallet).where(Wallet.id == wallet_id,
                                                          Wallet.user_id == user_id,
                                                          Wallet.is_active.is_(True),
                                                         Wallet.deleted_at.is_(None),
                                                         )
                                )


    @classmethod
    async def add_income(cls, wallet_name:str ,user_id: int, amount: Decimal, session: AsyncSession) -> Wallet | None:
        wallet = await cls._get_active_wallet(wallet_name, user_id, session)
        if wallet is None:
            return None
        wallet.balance += amount
        await session.flush()
        await session.refresh(wallet)
        return wallet

    @classmethod
    async def get_wallet_balance_by_name(cls, wallet_name: str, user_id:int, session: AsyncSession) -> Wallet | None:
        wallet = await WalletRepository._get_active_wallet(wallet_name, user_id, session)
        return wallet if wallet else None

    @classmethod
    async def add_expense(cls,wallet_name:str, user_id:int, amount: Decimal, session: AsyncSession) -> Wallet| None:

        wallet = await cls._get_active_wallet(wallet_name, user_id, session)
        if wallet is None:
            return None
        if wallet.balance < amount:
            raise InsufficientFunds()
        wallet.balance -= amount
        await session.flush()
        await session.refresh(wallet)
        return wallet


    @classmethod
    async def get_all_wallets(cls, user_id:int, session: AsyncSession) -> list[Wallet] | None:
        result = await session.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.is_active.is_(True),
                Wallet.deleted_at.is_(None)
            )
        )
        return list(result.scalars().all())



    @classmethod
    async def create_wallet(cls, data: WalletCreate,user_id:int, session: AsyncSession) -> Wallet:
        wallet  = Wallet(name=data.name, user_id=user_id, currency=data.currency)
        session.add(wallet)
        await session.commit()
        await session.refresh(wallet)
        return wallet

    @classmethod
    async def delete_wallet(cls, wallet_name: str,user_id: int, session: AsyncSession):
        wallet = await cls._get_active_wallet(wallet_name, user_id, session)
        if wallet is None:
            return None

        wallet.is_active = False
        wallet.deleted_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(wallet)
        return True

    @classmethod
    async def update_wallet(cls, wallet_name:str ,new_wallet_name:str,user_id:int, session: AsyncSession):
        wallet = await cls._get_active_wallet(wallet_name, user_id, session)
        if wallet is None:
            return None
        wallet.name = new_wallet_name
        await session.commit()
        await session.refresh(wallet)
        return wallet





    @classmethod
    async def _get_active_wallet(cls, wallet_name: str, user_id: int, session: AsyncSession) -> Wallet | None:
        return await session.scalar(
            select(Wallet)
            .where(Wallet.name == wallet_name,
                                 Wallet.user_id == user_id,
                                 Wallet.is_active.is_(True),
                                 Wallet.deleted_at.is_(None),

                                 )
            .with_for_update()
                   )