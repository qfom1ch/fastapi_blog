from typing import Sequence

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.user import security
from apps.user.models import User
from apps.user.schemas import UserCreate

from .base import UserRepository


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def create(self, user: UserCreate) -> User:
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=security.get_hash_password(user.password),
        )
        self._db_session.add(new_user)
        await self._db_session.commit()
        return new_user

    async def get_user(self, user_id: int) -> User | None:
        query = select(User).filter_by(id=user_id)
        result = await self._db_session.execute(query)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        query = select(User).filter_by(username=username)
        result = await self._db_session.execute(query)
        return result.scalars().first()

    async def get_all(self) -> Sequence[User]:
        query = select(User)
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def update(self, user_id: int, updated_user_params: dict) -> User | None:
        query = update(User).filter_by(id=user_id).values(**updated_user_params).returning(User)
        result = await self._db_session.execute(query)
        return result.scalars().first()

    async def delete(self, user_id: int) -> None:
        query = (
            update(User)
            .where(and_(User.id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.id)
        )
        result = await self._db_session.execute(query)
        return result.scalars().first()

    async def check_duplicate_email(self, email: str) -> bool:
        query = select(User).filter_by(email=email).exists()
        result = await self._db_session.execute(query.select())
        return result.scalars().first()

    async def check_duplicate_username(self, username: str) -> bool:
        query = select(User).filter_by(username=username).exists()
        result = await self._db_session.execute(query.select())
        return result.scalars().first()
