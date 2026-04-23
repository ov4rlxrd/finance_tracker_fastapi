from datetime import datetime

from app.api.dependencies.verified import VerifiedUser
from fastapi import APIRouter, Query

from app.api.dependencies.auth import CurrentUser
from app.database import SessionDep
from app.schemas.schemas import OperationRequest, OperationResponse, IternalTransferCreateSchema, TransferCreateSchema
from app.service import operation_service
from app.service.ai_service import get_operations_analysis

operations_router = APIRouter(tags=["operations"], prefix="/operations")

@operations_router.post("/income")
async def add_income(operation: OperationRequest,current_user: CurrentUser, session: SessionDep)-> OperationResponse:
    return await operation_service.add_income_service(operation, current_user.id, session)


@operations_router.post("/expense")
async def add_expense(operation: OperationRequest, current_user: CurrentUser, session: SessionDep)-> OperationResponse:
    return await operation_service.add_expense_service(operation, current_user.id, session)

@operations_router.get("")
async def get_operation_list(
        current_user: CurrentUser,
        session: SessionDep,
        wallet_id: int | None = Query(None),
        date_from: datetime | None = Query(None),
        date_to: datetime | None = Query(None),
)-> list[OperationResponse]:
    return await operation_service.get_operations_list_service(current_user.id, session, wallet_id, date_from, date_to)


@operations_router.post("/iternal_transfer")
async def create_iternal_transfer(current_user: CurrentUser, payload: IternalTransferCreateSchema, session: SessionDep) -> OperationResponse:
    return await operation_service.transfer_between_wallets_service(current_user.id,
                                                                    session,
                                                                    payload.from_wallet_id,
                                                                    payload.to_wallet_id,
                                                                    payload.amount,
    )

@operations_router.post("/transfer")
async def create_transfer(current_user: CurrentUser, payload: TransferCreateSchema, session: SessionDep)-> OperationResponse:
    return await operation_service.transfer_between_users_service(current_user.id,
                                                                  payload.to_user_id,
                                                                  payload.wallet_id,
                                                                  payload.amount,
                                                                  session)

@operations_router.get("/analysis/{wallet_id}")
async def get_analysis_for_wallet(current_user: CurrentUser, session: SessionDep, wallet_id: int, verified_user: VerifiedUser):
    return await get_operations_analysis(current_user.id, session, wallet_id)

@operations_router.get("/analysis")
async def get_analysis(current_user: CurrentUser, session: SessionDep, verified_user: VerifiedUser):
    return await get_operations_analysis(current_user.id, session,)