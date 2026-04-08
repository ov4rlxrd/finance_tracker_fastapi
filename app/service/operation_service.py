from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from starlette import status

from app.core.enums import OperationEnum
from app.exceptions.user import UserNotFound, NotAuthorized
from app.exceptions.wallet import WalletNotFound, TransferSameWallet, InsufficientFunds, CurrencyConversionError
from app.repository.users import UserRepository
from app.schemas.schemas import OperationRequest, OperationResponse
from app.repository.wallets import WalletRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.operations import OperationsRepository
from app.service.exhange_service import get_exchange_rate


async def add_income_service(operation: OperationRequest,user_id: int, session: AsyncSession) -> OperationResponse:
    if not await WalletRepository.is_wallet_exist(operation.wallet_name,user_id, session):
        raise WalletNotFound()
    wallet = await WalletRepository.add_income(operation.wallet_name, user_id, operation.amount, session)
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Noy authorized to update balance")
    new_operation = await OperationsRepository.create_operation(wallet_id=wallet.id, operation_type=OperationEnum.INCOME,
                                                            amount=operation.amount,currency=wallet.currency,category=operation.category,
                                                            session=session)
    await session.commit()
    await session.refresh(new_operation)
    return OperationResponse.model_validate(new_operation)

async def add_expense_service(operation: OperationRequest, user_id: int,session: AsyncSession) -> OperationResponse:
    if not await WalletRepository.is_wallet_exist(operation.wallet_name, user_id, session):
        raise WalletNotFound()
    try:
        wallet = await WalletRepository.add_expense(operation.wallet_name, user_id, operation.amount, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if wallet is None:
        raise NotAuthorized()
    new_operation = await OperationsRepository.create_operation(wallet_id=wallet.id, operation_type=OperationEnum.EXPENSE,
                                                            amount=operation.amount, currency=wallet.currency,category=operation.category,
                                                            session=session)
    await session.commit()
    await session.refresh(new_operation)
    return OperationResponse.model_validate(new_operation)

async def get_operations_list_service(
        user_id: int,
        session: AsyncSession,
        wallet_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
) -> list[OperationResponse]:
    if wallet_id:
        wallet = await WalletRepository.get_wallet_by_id(wallet_id, user_id, session)
        if not wallet:
            raise WalletNotFound()
        wallets_ids = [wallet.id]
    else:
        wallets = await WalletRepository.get_all_wallets(user_id, session)
        wallets_ids = [wallet.id for wallet in wallets]

    operations = await OperationsRepository.get_operations_list(session, wallets_ids, date_from, date_to)
    return [OperationResponse.model_validate(op) for op in operations]

async def transfer_between_wallets_service(
        user_id: int,
        session: AsyncSession,
        from_wallet_id: int,
        to_wallet_id: int,
        amount: Decimal,
) -> OperationResponse:
    from_wallet = await WalletRepository.get_wallet_by_id(from_wallet_id, user_id, session)
    to_wallet = await WalletRepository.get_wallet_by_id(to_wallet_id, user_id, session)

    if not from_wallet or not to_wallet:
        raise WalletNotFound()

    if from_wallet_id == to_wallet_id:
        raise TransferSameWallet()
    return await _execute_transfer(from_wallet, to_wallet, amount, session)


async def transfer_between_users_service(
        from_user_id: int,
        to_user_id: int,
        wallet_id: int,
        amount: Decimal,
    session: AsyncSession,
) -> OperationResponse:


    from_user = await UserRepository.find_by_id(from_user_id, session)
    to_user = await UserRepository.find_by_id(to_user_id, session)


    from_user_wallet = await WalletRepository.get_wallet_by_id(wallet_id, from_user_id, session)
    to_user_wallet = await WalletRepository.get_all_wallets(to_user_id, session)
    to_user_wallet = to_user_wallet[0] if to_user_wallet else None



    if not from_user or not to_user:
        raise UserNotFound()

    if not from_user_wallet or not to_user_wallet:
        raise WalletNotFound()

    if from_user_wallet.id == to_user_wallet.id:
        raise TransferSameWallet()

    return await _execute_transfer(from_user_wallet, to_user_wallet, amount, session)


async def _execute_transfer(
    from_wallet, to_wallet, amount, session
) -> OperationResponse:
    target_amount = amount
    if from_wallet.currency != to_wallet.currency:
        try:
            exchange_rate = await get_exchange_rate(from_wallet.currency, to_wallet.currency)
            target_amount = amount * exchange_rate
        except KeyError:
            raise CurrencyConversionError()

    if from_wallet.balance < amount:
        raise InsufficientFunds()

    from_wallet.balance -= amount
    to_wallet.balance += target_amount

    await OperationsRepository.create_operation(
        wallet_id=from_wallet.id,
        operation_type=OperationEnum.TRANSFER_OUT,
        amount=amount,
        currency=from_wallet.currency,
        category="Transfer",
        session=session
    )
    operation = await OperationsRepository.create_operation(
        wallet_id=to_wallet.id,
        operation_type=OperationEnum.TRANSFER_IN,
        amount=target_amount,
        currency=to_wallet.currency,
        category="Transfer",
        session=session
    )
    await session.commit()
    return OperationResponse.model_validate(operation)