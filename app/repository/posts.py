from datetime import datetime, timezone

from sqlalchemy import select, func, delete, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Post, PostLike, User
from app.schemas.schemas import PostCreate


class PostsRepository:

    @classmethod
    async def _get_post_by_id(cls, post_id:int,  user_id: int, session: AsyncSession) -> Post | None:
        return await session.scalar(
            select(Post)
            .where(Post.id == post_id,
                   Post.user_id == user_id,
                   Post.deleted_at.is_(None),

                   )
        )

    @classmethod
    async def _get_post_by_id_public(cls, post_id: int, session: AsyncSession) -> Post | None:
        return await session.scalar(
            select(Post)
            .where(
                Post.id == post_id,
                Post.deleted_at.is_(None),
            )
        )


    @classmethod
    async def _get_post_like(cls, post_id:int, user_id: int, session: AsyncSession) -> type[PostLike] | None:
        return await session.get(PostLike, (user_id,post_id))

    @classmethod
    async def is_post_exists(cls, post_id: int, user_id: int, session: AsyncSession) -> Post | None:
        post = await cls._get_post_by_id(post_id, user_id, session)
        return post is not None

    @classmethod
    async def create_post(cls, data: PostCreate, user_id:int, session: AsyncSession) -> Post:
        post = Post(title=data.title, text=data.text, user_id=user_id)
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @classmethod
    async def get_post_by_id(cls, post_id: int,user_id:int , session: AsyncSession) -> Post | None:
        return await session.scalar(select(Post).where(Post.id == post_id,
                                                         Post.user_id == user_id,
                                                         Post.deleted_at.is_(None),
                                                         )
    )

    @classmethod
    async def delete_post(cls, post_id:int, user_id: int, session: AsyncSession):
        post = await cls._get_post_by_id(post_id, user_id, session)
        if post is None:
            return None

        post.is_active = False
        post.deleted_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(post)
        return True

    @classmethod
    async def update_post(cls, post_id:int, new_title: str, new_text:str, user_id: int, session: AsyncSession):
        post = await cls._get_post_by_id(post_id, user_id, session)
        if post is None:
            return None
        post.title = new_title
        post.text = new_text
        await session.commit()
        await session.refresh(post)
        return post

    @classmethod
    async def like_post(cls, post_id:int, user_id: int, session: AsyncSession):
        like = PostLike(user_id=user_id, post_id=post_id)
        session.add(like)
        await session.commit()
        await session.refresh(like)
        return like


    @classmethod
    async def unlike_post(cls, post_id:int, user_id: int, session: AsyncSession):
        await session.execute(
            delete(PostLike).where(
                PostLike.post_id == post_id,
                PostLike.user_id == user_id,
            )
        )
        await session.commit()


    @classmethod
    async def get_post_likes(cls, post_id:int, session: AsyncSession):

        like_count = await session.scalar(
            select(func.count()).where(PostLike.post_id == post_id)
        )

        return like_count

    @classmethod
    async def list_posts(cls, session: AsyncSession, user_id:int, limit: int = 50, offset: int = 0):
        is_liked = (
            select(literal(True))
            .where(PostLike.post_id == Post.id, PostLike.user_id == user_id)
            .correlate(Post)
            .exists()
            .label("is_liked")
        )

        stmt = (
            select(Post,User, func.count(PostLike.user_id).label("likes"), is_liked)
            .outerjoin(PostLike, PostLike.post_id == Post.id)
            .join(User, User.id == Post.user_id)
            .where(Post.deleted_at.is_(None))
            .group_by(Post.id, User.id)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await session.execute(stmt)).all()
        return rows
