from datetime import datetime
from typing import Union

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify
from app.blog.models import Post
from app.blog.schemas import PostCreate, ShowPost
from app.user.models import User


async def _create_post(post: PostCreate, db_session: AsyncSession, current_user: User) -> ShowPost:
    new_post = Post(
        title=post.title,
        short_description=post.short_description,
        text=post.text,
        slug=slugify(post.title),
        author_id=current_user.id,
        published_at=datetime.now()
    )
    db_session.add(new_post)
    await db_session.flush()
    return new_post


async def _get_post_by_id(post_id: int, db_session: AsyncSession) -> Union[User, None]:
    query = select(Post).where(Post.id == post_id)
    res = await db_session.execute(query)
    post_row = res.fetchone()
    if post_row is not None:
        return post_row[0]


async def _get_post_by_slug(post_slug: str, db_session: AsyncSession) -> Union[User, None]:
    query = select(Post).where(Post.slug == post_slug)
    res = await db_session.execute(query)
    post_row = res.fetchone()
    if post_row is not None:
        return post_row[0]


async def _get_post_by_title(post_title: str, db_session: AsyncSession) -> Union[User, None]:
    query = select(Post).where(Post.title == post_title)
    res = await db_session.execute(query)
    post_row = res.fetchone()
    if post_row is not None:
        return post_row[0]


async def _get_posts_by_user_id(user_id: int, db_session: AsyncSession) -> list:
    query = select(Post).where(Post.author_id == user_id)
    res = await db_session.execute(query)
    user_posts = [post[0] for post in res.fetchall()]
    return user_posts


async def _get_all_posts(db_session: AsyncSession) -> list:
    query = select(Post)
    res = await db_session.execute(query)
    list_posts = [post[0] for post in res.fetchall()]
    return list_posts


async def _update_post(post_id: int,
                       updated_post_params: dict,
                       db_session: AsyncSession) -> Union[Post, None]:
    query = (
        update(Post)
        .where(Post.id == post_id)
        .values(**updated_post_params)
        .returning(Post)
    )
    res = await db_session.execute(query)
    update_post_row = res.fetchone()
    if update_post_row is not None:
        return update_post_row[0]


async def _delete_post(post_id: int, db_session: AsyncSession) -> None:
    query = delete(Post).where(Post.id == post_id)
    await db_session.execute(query)
