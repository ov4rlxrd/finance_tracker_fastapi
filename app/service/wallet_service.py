from decimal import Decimal

from app.core.enums import CurrencyEnum
from app.exceptions.wallet import WalletNotFound, WalletAlreadyExists, CurrencyConversionError
from app.repository.wallets import WalletRepository
from app.schemas.schemas import WalletCreate, WalletResponse, WalletUpdate, WalletTotalBalanceResponse
from app.service.exhange_service import get_exchange_rate
from sqlalchemy.ext.asyncio import AsyncSession


async def get_wallet(session: AsyncSession, user_id:int, wallet_name: str) -> WalletResponse:
    if not await WalletRepository.is_wallet_exist(wallet_name, user_id,session):
        raise WalletNotFound()

    wallet = await WalletRepository.get_wallet_balance_by_name(wallet_name,user_id, session)
    if wallet is None:
        raise WalletNotFound()
    return WalletResponse(id = wallet.id,name=wallet_name, balance=wallet.balance, currency=wallet.currency)


async def create_wallet(wallet: WalletCreate,user_id: int, session: AsyncSession) -> WalletResponse:
    if await WalletRepository.is_wallet_exist(wallet.name, user_id,session):
        raise WalletAlreadyExists()
    new_wallet = await WalletRepository.create_wallet(wallet, user_id, session)
    return WalletResponse.model_validate(new_wallet)


async def delete_wallet(wallet_name: str, user_id: int, session: AsyncSession) -> None:
    if not await WalletRepository.is_wallet_exist(wallet_name, user_id,session):
        raise WalletNotFound()
    await WalletRepository.delete_wallet(wallet_name, user_id, session)

async def update_wallet(wallet: WalletUpdate, user_id: int, session: AsyncSession) -> WalletResponse:
    if not await WalletRepository.is_wallet_exist(wallet.old_name, user_id,session):
        raise WalletNotFound()
    return await WalletRepository.update_wallet(wallet.old_name,wallet.new_name, user_id, session)

async def get_total_balance(user_id: int, session: AsyncSession) -> WalletTotalBalanceResponse:
    wallets = await WalletRepository.get_all_wallets(user_id, session)
    if not wallets:
        raise WalletNotFound()
    total_balance = Decimal("0")
    for wallet in wallets:
        if wallet.currency == CurrencyEnum.RUB:
            total_balance += wallet.balance
        else:
            try:
                exchange_rate = await get_exchange_rate(wallet.currency, CurrencyEnum.RUB)
            except KeyError:
                raise CurrencyConversionError()
            total_balance += wallet.balance * exchange_rate
    return WalletTotalBalanceResponse(name="Total Balance", balance=total_balance, currency=CurrencyEnum.RUB)
