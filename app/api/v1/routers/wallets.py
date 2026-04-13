from fastapi import APIRouter
from starlette import status

from app.api.dependencies.auth import CurrentUser
from app.database import SessionDep
from app.schemas.schemas import WalletResponse, WalletCreate, WalletResponse, WalletDelete, WalletUpdate, \
    WalletTotalBalanceResponse
from app.service import wallet_service as wallets_service

wallets_router = APIRouter(tags=["wallets"], prefix="/wallets")




@wallets_router.get("/balance", status_code=status.HTTP_200_OK)
async def get_total_balance(current_user:CurrentUser, session: SessionDep)->WalletTotalBalanceResponse:
    return await wallets_service.get_total_balance(current_user.id, session)

@wallets_router.get("/{wallet_name}", status_code=status.HTTP_200_OK)
async def get_wallet(session:SessionDep,current_user: CurrentUser, wallet_name: str) -> WalletResponse:
    return await wallets_service.get_wallet(session,current_user.id, wallet_name)


@wallets_router.post("", status_code=status.HTTP_200_OK)
async def create_wallet(wallet: WalletCreate, current_user:CurrentUser, session: SessionDep)->WalletResponse:
    return await wallets_service.create_wallet(wallet, current_user.id, session)

@wallets_router.delete("/{wallet_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wallet(wallet_name: str, current_user:CurrentUser, session: SessionDep) -> None:
    await wallets_service.delete_wallet(wallet_name, current_user.id, session)

@wallets_router.patch("" , status_code=status.HTTP_200_OK)
async def update_wallet(wallet: WalletUpdate, current_user:CurrentUser, session: SessionDep)->WalletResponse:
    return await wallets_service.update_wallet(wallet, current_user.id, session)
