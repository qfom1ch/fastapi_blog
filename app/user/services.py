from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.user.schemas import UserCreate, ShowUser
from app.user.models import User

from sqlalchemy import update, and_, select


async def _get_user_by_id(user_id: int, db_session: AsyncSession) -> Union[User, None]:
    query = select(User).where(User.id == user_id)
    res = await db_session.execute(query)
    user_row = res.fetchone()
    if user_row is not None:
        return user_row[0]


async def _get_user_by_email(email: str, db_session: AsyncSession) -> Union[User, None]:
    query = select(User).where(User.email == email)
    res = await db_session.execute(query)
    user_row = res.fetchone()
    if user_row is not None:
        return user_row[0]


async def _get_user_by_username(username: str, db_session: AsyncSession) -> Union[User, None]:
    query = select(User).where(User.username == username)
    res = await db_session.execute(query)
    user_row = res.fetchone()
    if user_row is not None:
        return user_row[0]


async def _create_user(user: UserCreate, db_session: AsyncSession) -> ShowUser:
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password,
    )
    db_session.add(new_user)
    await db_session.flush()
    return new_user


async def _check_duplicate_email(user_email: dict, db_session: AsyncSession) -> bool:
    stmt = select(User.email).where(User.email == user_email).exists()
    res = await db_session.execute(stmt.select())
    res_row = res.fetchone()
    return res_row[0]


async def _check_duplicate_username(user_username: dict, db_session: AsyncSession) -> bool:
    stmt = select(User.username).where(User.username == user_username).exists()
    res = await db_session.execute(stmt.select())
    res_row = res.fetchone()
    return res_row[0]


async def _update_user(user_id: id,
                       updated_user_params: dict,
                       db_session: AsyncSession) -> Union[User, None]:
    if updated_user_params.get('password'):
        updated_user_params['hashed_password'] = updated_user_params.pop('password')

    query = (
        update(User)
        .where(and_(User.id == user_id, User.is_active == True))
        .values(**updated_user_params)
        .returning(User)
    )
    res = await db_session.execute(query)
    update_user_row = res.fetchone()
    if update_user_row is not None:
        return update_user_row[0]


async def _delete_user(user_id: int, db_session: AsyncSession) -> Union[int, None]:
    query = (
        update(User)
        .where(and_(User.id == user_id, User.is_active == True))
        .values(is_active=False)
        .returning(User.id)
    )
    res = await db_session.execute(query)
    deleted_user_id_row = res.fetchone()
    if deleted_user_id_row is not None:
        return deleted_user_id_row[0]
