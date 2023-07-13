from sqlalchemy.ext.asyncio import AsyncSession

from app.user.schemas import UserCreate, ShowUser
from app.user.models import User

async def create_user(db_session: AsyncSession, user: UserCreate):
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password,
    )
    db_session.add(new_user)
    await db_session.flush()
    return ShowUser(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_active=new_user.is_active,
        is_admin=new_user.is_admin,
        is_superuser=new_user.is_superuser,
    )
