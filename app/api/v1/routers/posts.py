from fastapi import APIRouter
from starlette import status

from app.api.dependencies.auth import CurrentUser
from app.database import SessionDep
from app.schemas.schemas import PostCreate, PostResponseBase, PostUpdate, PostResponseLikes, PostListItem
import app.service.post_service as post_service

posts_router = APIRouter(tags=["posts"], prefix="/posts")




@posts_router.get("", status_code=status.HTTP_200_OK)
async def list_posts(current_user:CurrentUser, session: SessionDep, limit: int = 50, offset: int = 0) -> list[PostListItem]:
    return await post_service.list_posts_service(session, current_user.id, limit=limit, offset=offset)

@posts_router.post("", status_code=status.HTTP_200_OK)
async def create_post(post: PostCreate, current_user:CurrentUser, session: SessionDep)->PostResponseBase:
    return await post_service.create_post(post, current_user.id, session)


@posts_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, current_user:CurrentUser, session: SessionDep) -> None:
    await post_service.delete_post_service(post_id, current_user.id, session)

@posts_router.patch("" , status_code=status.HTTP_200_OK)
async def update_post(post: PostUpdate, current_user:CurrentUser, session: SessionDep)->PostResponseBase:
    return await post_service.update_post_service(post, current_user.id, session)

@posts_router.get("/{post_id}", status_code=status.HTTP_200_OK)
async def get_post(post_id: int, current_user:CurrentUser, session: SessionDep)->PostResponseLikes:
    return await post_service.get_post_service(post_id, current_user.id, session)

@posts_router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
async def like_post(post_id: int, current_user:CurrentUser, session: SessionDep):
    return await post_service.post_like(post_id, current_user.id, session)

@posts_router.delete("/{post_id}/like")
async def unlike_post(post_id: int, current_user:CurrentUser, session: SessionDep):
    return await post_service.unlike_post(post_id, current_user.id, session)