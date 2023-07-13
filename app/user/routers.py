from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.user.schemas import UserCreate, ShowUser
from app.user.services import create_user
from db.session import get_db

user_router = APIRouter(
    prefix='/users',
    tags=['users']
)

@user_router.post("/", response_model=ShowUser)
async def create_new_user(user: UserCreate, db_session: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await create_user(user=user, db_session=db_session)
    except IntegrityError as err:
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
