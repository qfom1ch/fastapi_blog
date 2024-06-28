from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config import ALGORITHM, SECRET_KEY
from db.session import get_db

from .repository.sqlalchemy import SQLAlchemyUserRepository
from .security import oauth2_scheme
from .service import UserService


async def get_user_service_sqlalchemy(db_session: AsyncSession = Depends(get_db)) -> UserService:
    sqlalchemy_user_repository = SQLAlchemyUserRepository(db_session=db_session)
    return UserService(user_repository=sqlalchemy_user_repository)


async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme),
        user_service: UserService = Depends(get_user_service_sqlalchemy),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await user_service.get_by_username(username)
    if result.data is None:
        raise credentials_exception
    return result.data
