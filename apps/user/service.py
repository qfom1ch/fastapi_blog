from datetime import timedelta

from fastapi import status
from jose import JWTError, jwt

from apps.user import security
from apps.user.models import User
from apps.user.schemas import UpdateUserRequest, UserCreate
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from tasks.tasks import send_email_for_verification

from .repository.base import UserRepository
from .schemas import UserServiceResult


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def create(self, user: UserCreate) -> UserServiceResult:
        if await self._user_repository.check_duplicate_email(email=user.email):
            return UserServiceResult(
                success=False, status_code=status.HTTP_409_CONFLICT,
                detail="This email is already registered",
            )
        if await self._user_repository.check_duplicate_username(username=user.username):
            return UserServiceResult(
                success=False, status_code=status.HTTP_409_CONFLICT,
                detail="This username is already registered",
            )

        new_user = await self._user_repository.create(user=user)
        send_email_for_verification.delay(user.username, user.email)

        return UserServiceResult(success=True, status_code=status.HTTP_200_OK, data=new_user)

    async def get_user(self, user_id: int) -> UserServiceResult:
        user = await self._get_user_or_404(user_id=user_id)
        if isinstance(user, UserServiceResult):
            return user

        return UserServiceResult(success=True, status_code=status.HTTP_200_OK, data=user)

    async def get_by_username(self, username: str) -> UserServiceResult:
        user = await self._user_repository.get_by_username(username=username)
        if not user:
            return UserServiceResult(
                success=False, status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        return UserServiceResult(success=True, status_code=status.HTTP_200_OK, data=user)

    async def get_all(self) -> UserServiceResult:
        users = await self._user_repository.get_all()
        return UserServiceResult(success=True, status_code=status.HTTP_200_OK, data=users)

    async def update(self, user_id: int, data_to_update: UpdateUserRequest, current_user: User) -> UserServiceResult:
        user_for_update = await self._user_repository.get_user(user_id=user_id)

        if not user_for_update:
            return UserServiceResult(
                success=False, status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found."
            )

        updated_user_params = data_to_update.model_dump(exclude_none=True)

        if not updated_user_params:
            return UserServiceResult(
                success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one parameter for user update info should be provided",
            )

        if email := updated_user_params.get('email'):
            if await self._user_repository.check_duplicate_email(email=email):
                return UserServiceResult(
                    success=False, status_code=status.HTTP_409_CONFLICT,
                    detail="This email is already registered",
                )

        if username := updated_user_params.get('username'):
            if await self._user_repository.check_duplicate_username(username=username):
                return UserServiceResult(
                    success=False, status_code=status.HTTP_409_CONFLICT,
                    detail="This username is already registered",
                )

        if user_id != current_user.id:
            if not await security.check_user_permissions(target_user=user_for_update, current_user=current_user):
                return UserServiceResult(
                    success=False, status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden.",
                )

        if updated_user_params.get('password'):
            updated_user_params['hashed_password'] = security.get_hash_password(updated_user_params.pop('password'))

        updated_user = await self._user_repository.update(user_id=user_id, updated_user_params=updated_user_params)
        return UserServiceResult(success=True, status_code=status.HTTP_200_OK, data=updated_user)

    async def delete(self, user_id: int, current_user: User) -> UserServiceResult:
        user_for_del = await self._get_user_or_404(user_id=user_id)
        if isinstance(user_for_del, UserServiceResult):
            return user_for_del

        if not security.check_user_permissions(target_user=user_for_del, current_user=current_user):
            return UserServiceResult(
                success=False, status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden.",
            )

        await self._user_repository.delete(user_id=user_id)
        return UserServiceResult(success=True, status_code=status.HTTP_200_OK)

    async def login_for_access_token(self, username: str, password: str) -> UserServiceResult:
        user = await self._user_repository.get_by_username(username=username)
        verify_pass = security.verify_password(password, user.hashed_password)

        if not user or not verify_pass:
            return UserServiceResult(
                success=False, status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires,
        )
        token_data = {"access_token": access_token, "token_type": "bearer"}

        return UserServiceResult(success=True, status_code=status.HTTP_200_OK, data=token_data)

    async def email_verification(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            user = await self._user_repository.get_by_username(username=username)
        except JWTError:
            return UserServiceResult(
                success=False, status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        if not user:
            return UserServiceResult(
                success=False, status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user_params = {"is_verified_email": True}

        await self._user_repository.update(user_id=user.id, updated_user_params=user_params)

    async def add_admin_privilege(self, user_id: int, current_user: User):
        if not current_user.is_superuser:
            return UserServiceResult(
                success=False, status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden.",
            )
        if current_user.id == user_id:
            return UserServiceResult(
                success=False, status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot manage privileges of itself.",
            )

        user_for_promotion = await self._get_user_or_404(user_id=user_id)
        if isinstance(user_for_promotion, UserServiceResult):
            return user_for_promotion

        if user_for_promotion.is_admin or user_for_promotion.is_superuser:
            return UserServiceResult(
                success=False, status_code=status.HTTP_409_CONFLICT,
                detail=f"User with id {user_id} already promoted to admin / superadmin.",
            )

        updated_user_params = {"is_admin": True}
        user = await self._user_repository.update(user_id=user_id, updated_user_params=updated_user_params)

        return UserServiceResult(success=True, status_code=status.HTTP_200_OK, data=user)

    async def remove_admin_privilege(self, user_id: int, current_user: User):
        if not current_user.is_superuser:
            return UserServiceResult(
                success=False, status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden.",
            )
        if current_user.id == user_id:
            return UserServiceResult(
                success=False, status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot manage privileges of itself.",
            )

        user_for_downgrade = await self._get_user_or_404(user_id=user_id)
        if isinstance(user_for_downgrade, UserServiceResult):
            return user_for_downgrade

        if user_for_downgrade.is_superuser:
            return UserServiceResult(
                success=False, status_code=status.HTTP_409_CONFLICT,
                detail="Superuser privileges cannot be changed",
            )

        if not user_for_downgrade.is_admin:
            return UserServiceResult(
                success=False, status_code=status.HTTP_409_CONFLICT,
                detail=f"User with id {user_id} has no admin privileges.",
            )

        updated_user_params = {"is_admin": False}
        user = await self._user_repository.update(user_id=user_id, updated_user_params=updated_user_params)

        return UserServiceResult(success=True, status_code=status.HTTP_200_OK, data=user)

    async def _get_user_or_404(self, user_id: int) -> User | UserServiceResult:
        user = await self._user_repository.get_user(user_id=user_id)
        if not user:
            return UserServiceResult(
                success=False, status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user
