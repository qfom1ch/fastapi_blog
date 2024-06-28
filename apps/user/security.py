from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from apps.user.models import User
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

pwd_context: Any = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme: Any = OAuth2PasswordBearer(tokenUrl="/users/token")


def get_hash_password(password: str) -> Any:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> Any:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


async def check_user_permissions(target_user: User, current_user: User) -> bool:
    if current_user.id == target_user.id:
        if current_user.is_superuser:
            return False
    elif current_user.id != target_user.id:
        if not current_user.is_admin and not current_user.is_superuser:
            return False
        elif current_user.is_superuser and target_user.is_superuser:
            return False
        elif (current_user.is_admin and not current_user.is_superuser) \
                and (target_user.is_admin and not target_user.is_superuser):
            return False
        elif (current_user.is_admin and not current_user.is_superuser) and target_user.is_superuser:
            return False
    return True
