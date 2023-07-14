from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi import status
from db.session import get_db
from app.user.schemas import UserCreate, ShowUser, DeleteUserResponse, UpdateUserRequest, UpdatedUserResponse
from app.user.services import (_create_user,
                               _delete_user,
                               _get_user_by_id,
                               _get_user_by_email,
                               _get_user_by_username,
                               _update_user,
                               _check_duplicate_email,
                               _check_duplicate_username)

user_router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(user_id: int = None,
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
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Not enough data."
        )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found."
        )
    return user


@user_router.post("/", response_model=ShowUser)
async def create_user(user: UserCreate, db_session: AsyncSession = Depends(get_db)) -> ShowUser:
    user_data = user.model_dump()
    if await _check_duplicate_email(user_data['email'], db_session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='This email is already registered'
        )
    if await _check_duplicate_username(user_data['username'], db_session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='This username is already registered'
        )
    return await _create_user(user, db_session)


@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(user_id: int,
                            data_to_update: UpdateUserRequest,
                            db_session: AsyncSession = Depends(get_db)) -> UpdatedUserResponse:
    updated_user_params = data_to_update.model_dump(exclude_none=True)
    if updated_user_params == {}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one parameter for user update info should be provided",
        )
    user_for_update = await _get_user_by_id(user_id, db_session)
    if user_for_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found."
        )
    updated_user = await _update_user(user_id, updated_user_params, db_session)
    return updated_user


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(user_id: int, db_session: AsyncSession = Depends(get_db)) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db_session)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found."
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)
