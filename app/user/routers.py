from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from fastapi_pagination import Page, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.models import User
from app.user.schemas import (DeleteUserResponse, ShowUser, Token,
                              UpdatedUserResponse, UpdateUserRequest,
                              UserCreate)
from app.user.security import authenticate_user, create_access_token
from app.user.services import (_check_duplicate_email,
                               _check_duplicate_username,
                               _check_user_permissions, _create_user,
                               _delete_user, _get_user_by_email,
                               _get_user_by_id, _get_user_by_username,
                               _get_users, _update_user)
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from db.session import get_db
from tasks.tasks import send_email_for_verification

from ..blog.schemas import ShowPost
from ..blog.services import _get_posts_by_user_id
from . import security

user_router = APIRouter(
    prefix='/users',
)


@user_router.get("/", response_model=ShowUser, tags=['Users'])
async def get_user(user_id: int = None,
                   user_email: str = None,
                   username: str = None,
                   db_session: AsyncSession = Depends(get_db)) -> ShowUser:
    if user_id:
        user = await _get_user_by_id(user_id, db_session)
    elif user_email:
        user = await _get_user_by_email(user_email, db_session)
    elif username:
        user = await _get_user_by_username(username, db_session)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not enough data."
        )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return user


@user_router.get("/list", response_model=Page[ShowUser], tags=['Users'])
@cache(expire=60)
async def list_users(db_session: AsyncSession = Depends(get_db)):
    users = await _get_users(db_session)
    return paginate(users)


@user_router.get("/me/posts", response_model=Page[ShowPost], tags=['Users'])
async def get_own_posts(
        current_user: User = Depends(security.get_current_user_from_token),
        db_session: AsyncSession = Depends(get_db)) -> Page[ShowPost]:
    user_id = current_user.id
    user_posts = await _get_posts_by_user_id(user_id, db_session)
    return paginate(user_posts)


@user_router.post("/", response_model=ShowUser, tags=['Users'])
async def create_user(user: UserCreate,
                      db_session: AsyncSession = Depends(get_db)) -> ShowUser:
    if await _check_duplicate_email(user.email, db_session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='This email is already registered'
        )
    if await _check_duplicate_username(user.username, db_session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='This username is already registered'
        )
    send_email_for_verification.delay(user.username, user.email)
    return await _create_user(user, db_session)


@user_router.patch("/", response_model=UpdatedUserResponse, tags=['Users'])
async def update_user_by_id(user_id: int,
                            data_to_update: UpdateUserRequest,
                            db_session: AsyncSession = Depends(get_db),
                            current_user:
                            User =
                            Depends(security.get_current_user_from_token)) \
        -> UpdatedUserResponse:
    updated_user_params = data_to_update.model_dump(exclude_none=True)
    if updated_user_params == {}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("At least one parameter for user update"
                    " info should be provided"),
        )
    if updated_user_params.get('email'):
        if await _check_duplicate_email(updated_user_params['email'],
                                        db_session):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='This email is already registered'
            )
    if updated_user_params.get('username'):
        if await _check_duplicate_username(updated_user_params['username'],
                                           db_session):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='This username is already registered'
            )
    user_for_update = await _get_user_by_id(user_id, db_session)
    if user_for_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    if user_id != current_user.id:
        if not _check_user_permissions(target_user=user_for_update,
                                       current_user=current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden.")
    updated_user = await _update_user(user_id, updated_user_params, db_session)
    return updated_user


@user_router.delete("/", response_model=DeleteUserResponse, tags=['Users'])
async def delete_user(user_id: int,
                      db_session: AsyncSession = Depends(get_db),
                      current_user:
                      User = Depends(security.get_current_user_from_token)) \
        -> DeleteUserResponse:
    user_for_deletion = await _get_user_by_id(user_id, db_session)
    if user_for_deletion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    if not _check_user_permissions(user_for_deletion, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden.")
    deleted_user_id = await _delete_user(user_id, db_session)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.patch("/give_admin_privileges", response_model=ShowUser,
                   tags=['Users privileges'])
async def add_admin_privilege(
        user_id: int,
        db_session: AsyncSession = Depends(get_db),
        current_user: User = Depends(security.get_current_user_from_token),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden.")
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot manage privileges of itself."
        )
    user_for_promotion = await _get_user_by_id(user_id, db_session)
    if user_for_promotion.is_admin or user_for_promotion.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(f"User with id {user_id} "
                    "already promoted to admin / superadmin."),
        )
    if user_for_promotion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    updated_user_params = {"is_admin": True}
    updated_user = await _update_user(user_id,
                                      updated_user_params,
                                      db_session)
    return updated_user


@user_router.delete("/remove_admin_privileges", response_model=ShowUser,
                    tags=['Users privileges'])
async def remove_admin_privilege(
        user_id: int,
        db_session: AsyncSession = Depends(get_db),
        current_user: User = Depends(security.get_current_user_from_token),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden.")
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot manage privileges of itself."
        )
    user_for_downgrade = await _get_user_by_id(user_id, db_session)
    if user_for_downgrade.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Superuser privileges cannot be changed",
        )

    if not user_for_downgrade.is_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with id {user_id} has no admin privileges.",
        )
    if user_for_downgrade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    updated_user_params = {"is_admin": False}
    updated_user = await _update_user(user_id,
                                      updated_user_params,
                                      db_session)
    return updated_user


@user_router.post("/token", response_model=Token, tags=["Login"])
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm =
                                 Depends(),
                                 db_session: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password,
                                   db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    token_data = {"access_token": access_token, "token_type": "bearer"}
    response.set_cookie(
        key="token",
        value=access_token,
        max_age=access_token_expires.total_seconds(),
        httponly=True,
    )
    return token_data


@user_router.get('/verification_email', tags=['Verification'])
async def email_verification(token: str,
                             db_session: AsyncSession = Depends(get_db)) \
        -> dict:
    user = await security.verify_token(token, db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")
    user_params = {"is_verified_email": True}
    await _update_user(user.id, user_params, db_session)
    return {"status_code": status.HTTP_200_OK, "success": True}
