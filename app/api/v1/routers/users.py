from typing import Annotated

from app.api.dependencies.auth import CurrentUser
from app.database import SessionDep
from app.schemas.schemas import UserCreate, UserResponse, UserUpdate, ForgotPasswordRequest, ResetPasswordRequest, \
    ChangePasswordRequest
from app.service.auth_service import login_for_access_token_service
from app.service.user_service import create_user, delete_user_service, update_user_service, \
    forgot_password_service, reset_password_service, change_password_service
from app.utils.email_utils import send_password_reset_email
from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post("", status_code=status.HTTP_201_CREATED)
async def add_user(user: UserCreate, session: SessionDep) -> UserResponse:
    return await create_user(user, session)


@users_router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDep
):
    return await login_for_access_token_service(username=form_data.username, password=form_data.password, session=session)

@users_router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(current_user: CurrentUser):
    return current_user

@users_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user:CurrentUser, session: SessionDep):
    return await delete_user_service(current_user.id, session)

@users_router.patch("/me", status_code=status.HTTP_200_OK)
async def update_user(current_user:CurrentUser, session: SessionDep, user_data: UserUpdate) -> UserResponse:
    return await update_user_service(user_data, current_user.id, session)


@users_router.post('/forgot-password', status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
        request_data: ForgotPasswordRequest,
        background_tasks: BackgroundTasks,
        session: SessionDep,
):
    payload = await forgot_password_service(request_data.email, session)
    if payload:
        background_tasks.add_task(
            send_password_reset_email,
            to_email=request_data.email,
            username=payload.username,
            token=payload.token,
        )
    return {"message": "If an account exists with this email, you will receive password reset instructions"}


@users_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
        request_data: ResetPasswordRequest,
        session: SessionDep,
):
    await reset_password_service(request_data.token,request_data.new_password,session)
    return {"message": 'Password reset successfully!'}


@users_router.patch("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
        password_data: ChangePasswordRequest,
        current_user: CurrentUser,
        session: SessionDep,
):
    await change_password_service(password_data.current_password, password_data.new_password, current_user.id, session)
    return {"message": "Password changed successfully!"}