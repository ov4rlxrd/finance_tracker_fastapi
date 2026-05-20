from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schemas import PostCreate, PostResponseBase, PostUpdate, PostResponseLikes, PostListItem
from app.repository.posts import PostsRepository


async def create_post(post: PostCreate,user_id: int, session: AsyncSession) -> PostResponseBase:
    new_post = await PostsRepository.create_post(post, user_id, session)
    return PostResponseBase.model_validate(new_post)



async def delete_post_service(post_id: int, user_id: int, session: AsyncSession) -> None:
    return await PostsRepository.delete_post(post_id, user_id, session)


async def update_post_service(post_update: PostUpdate, user_id: int, session: AsyncSession) -> PostResponseBase:
    return await PostsRepository.update_post(post_update.id, post_update.title, post_update.text, user_id, session)


async def post_like(post_id: int, user_id: int, session: AsyncSession):
    post = await PostsRepository._get_post_by_id_public(post_id, session)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = await PostsRepository._get_post_like(post.id, user_id, session)
    if existing:
        raise HTTPException(status_code=400, detail="Already liked")

    await PostsRepository.like_post(post.id, user_id, session)
    return {"details": "Post liked successfully"}

async def unlike_post(post_id: int, user_id: int, session: AsyncSession):
    post = await PostsRepository._get_post_by_id_public(post_id, session)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = await PostsRepository._get_post_like(post.id, user_id, session)
    if not existing:
        raise HTTPException(status_code=400, detail="Like not found")

    await PostsRepository.unlike_post(post.id, user_id, session)
    return {"details": "Post unliked successfully"}

async def get_post_service(post_id: int, user_id: int, session: AsyncSession) -> PostResponseLikes:
    post = await PostsRepository._get_post_by_id_public(post_id, session)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = await PostsRepository.get_post_likes(post_id, session)
    return PostResponseLikes(id=post.id, title=post.title, text=post.text, likes=likes)

async def list_posts_service(session: AsyncSession, user_id:int,  limit: int = 50, offset: int = 0):
    rows = await PostsRepository.list_posts(session, user_id, limit=limit, offset=offset)
    return [
        PostListItem(
            id=post.id,
            title=post.title,
            text=post.text,
            user_id=post.user_id,
            created_at=post.created_at,
            likes=likes,
            username=user.username,
            is_liked=is_liked,
        )
        for post, user, likes, is_liked in rows
    ]
