from fastapi import APIRouter
from starlette import status

from app.api.dependencies.roles import AdminUser
from app.database import SessionDep
from app.schemas.schemas import UserResponse, UserAdminResponse
from app.service.user_service import find_user, delete_user_service

admin_router = APIRouter(prefix="/admin", tags=["admin"])



@admin_router.get("/{user_id}")
async def find_user_by_id(user_id:int, session: SessionDep, _: AdminUser) -> UserAdminResponse | None:
    return await find_user(user_id, session)

@admin_router.delete("/{user_id}")
async def admin_deactivate_user(user_id: int, session: SessionDep, _: AdminUser) -> None:
    await delete_user_service(user_id, session)