from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from fastapi_pagination import Page, paginate

import apps.user.depends
from apps.user.depends import get_user_service_sqlalchemy
from apps.user.models import User
from apps.user.schemas import (ShowUser, Token, UpdatedUserResponse,
                               UpdateUserRequest, UserCreate,
                               UserServiceResult)
from apps.user.service import UserService

user_router = APIRouter(
    prefix='/users',
)


@user_router.get("/", response_model=ShowUser, tags=['Users'])
async def get_user(user_id: int, user_service: UserService = Depends(get_user_service_sqlalchemy)) -> ShowUser:
    get_user_result: UserServiceResult = await user_service.get_user(user_id=user_id)

    if not get_user_result.success:
        raise HTTPException(
            status_code=get_user_result.status_code,
            detail=get_user_result.detail,
        )

    return get_user_result.data


@user_router.get("/username", response_model=ShowUser, tags=['Users'])
async def get_by_username(username: str, user_service: UserService = Depends(get_user_service_sqlalchemy)) -> ShowUser:
    get_user_result: UserServiceResult = await user_service.get_by_username(username=username)

    if not get_user_result.success:
        raise HTTPException(
            status_code=get_user_result.status_code,
            detail=get_user_result.detail,
        )

    return get_user_result.data


@user_router.get("/list", response_model=Page[ShowUser], tags=['Users'])
@cache(expire=60)
async def get_all(user_service: UserService = Depends(get_user_service_sqlalchemy)):
    users_result: UserServiceResult = await user_service.get_all()
    return paginate(users_result.data)


@user_router.post("/", response_model=ShowUser, tags=['Users'])
async def create_user(user: UserCreate, user_service: UserService = Depends(get_user_service_sqlalchemy)) -> ShowUser:
    create_result: UserServiceResult = await user_service.create(user=user)

    if not create_result.success:
        raise HTTPException(
            status_code=create_result.status_code,
            detail=create_result.detail,
        )

    return create_result.data


@user_router.patch("/", response_model=UpdatedUserResponse, tags=['Users'])
async def update(
        user_id: int, data_to_update: UpdateUserRequest,
        current_user: User = Depends(apps.user.depends.get_current_user_from_token),
        user_service: UserService = Depends(get_user_service_sqlalchemy),
) -> UpdatedUserResponse:
    update_result: UserServiceResult = await user_service.update(
        user_id=user_id, data_to_update=data_to_update, current_user=current_user
    )

    if not update_result.success:
        raise HTTPException(
            status_code=update_result.status_code,
            detail=update_result.detail,
        )

    return update_result.data


@user_router.delete("/", status_code=status.HTTP_204_NO_CONTENT, tags=['Users'])
async def delete(
        user_id: int,
        current_user: User = Depends(apps.user.depends.get_current_user_from_token),
        user_service: UserService = Depends(get_user_service_sqlalchemy),
) -> Response:
    delete_result: UserServiceResult = await user_service.delete(user_id=user_id, current_user=current_user)

    if not delete_result.success:
        raise HTTPException(
            status_code=delete_result.status_code,
            detail=delete_result.detail,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.patch("/give_admin_privileges", response_model=ShowUser, tags=['Users privileges'])
async def add_admin_privilege(
        user_id: int,
        current_user: User = Depends(apps.user.depends.get_current_user_from_token),
        user_service: UserService = Depends(get_user_service_sqlalchemy),
):
    add_priv_result: UserServiceResult = await user_service.add_admin_privilege(
        user_id=user_id, current_user=current_user,
    )

    if not add_priv_result.success:
        raise HTTPException(
            status_code=add_priv_result.status_code,
            detail=add_priv_result.detail,
        )

    return add_priv_result.data


@user_router.patch("/remove_admin_privileges", response_model=ShowUser, tags=['Users privileges'])
async def remove_admin_privilege(
        user_id: int,
        current_user: User = Depends(apps.user.depends.get_current_user_from_token),
        user_service: UserService = Depends(get_user_service_sqlalchemy),
):
    remove_priv_result: UserServiceResult = await user_service.remove_admin_privilege(
        user_id=user_id, current_user=current_user,
    )

    if not remove_priv_result.success:
        raise HTTPException(
            status_code=remove_priv_result.status_code,
            detail=remove_priv_result.detail,
        )

    return remove_priv_result.data


@user_router.post("/token", response_model=Token, tags=["Login"])
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(get_user_service_sqlalchemy),
):
    login_result: UserServiceResult = await user_service.login_for_access_token(
        username=form_data.username, password=form_data.password,
    )

    if not login_result.success:
        raise HTTPException(
            status_code=login_result.status_code,
            detail=login_result.detail,
        )

    return login_result.data


@user_router.get('/verification_email', status_code=status.HTTP_200_OK, tags=['Verification'])
async def email_verification(token: str, user_service: UserService = Depends(get_user_service_sqlalchemy)) -> Response:
    verification_result: UserServiceResult = await user_service.email_verification(token=token)

    if not verification_result.success:
        raise HTTPException(
            status_code=verification_result.status_code,
            detail=verification_result.detail,
        )

    return Response(status_code=status.HTTP_200_OK)
