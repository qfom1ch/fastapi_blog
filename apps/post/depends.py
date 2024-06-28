from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db

from .repository.sqlalchemy import SQLAlchemyPostRepository
from .service import PostService


async def get_post_service_sqlalchemy(db_session: AsyncSession = Depends(get_db)) -> PostService:
    sqlalchemy_post_repository = SQLAlchemyPostRepository(db_session=db_session)
    return PostService(post_repository=sqlalchemy_post_repository)
