from datetime import datetime
from typing import Sequence

from slugify import slugify
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.post.models import Post
from apps.post.schemas import PostCreate
from apps.user.models import User

from .base import PostRepository


class SQLAlchemyPostRepository(PostRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def create(self, post: PostCreate, current_user: User) -> Post:
        new_post = Post(
            title=post.title,
            short_description=post.short_description,
            text=post.text,
            slug=slugify(post.title),
            author_id=current_user.id,
            published_at=datetime.now()
        )
        self._db_session.add(new_post)
        await self._db_session.commit()
        return new_post

    async def get_post(self, post_id: int) -> Post | None:
        query = select(Post).filter_by(id=post_id)
        result = await self._db_session.execute(query)
        return result.scalars().first()

    async def get_by_user_id(self, user_id: int) -> Sequence[Post]:
        query = select(Post).filter_by(author_id=user_id)
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def get_all(self) -> Sequence[Post]:
        query = select(Post)
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def update(self, post_id: int, updated_post_params: dict) -> Post | None:
        query = update(Post).filter_by(id=post_id).values(**updated_post_params).returning(Post)
        result = await self._db_session.execute(query)
        return result.scalars().first()

    async def delete(self, post_id: int) -> None:
        query = delete(Post).filter_by(id=post_id)
        await self._db_session.execute(query)
