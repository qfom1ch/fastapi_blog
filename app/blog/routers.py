from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi_cache.decorator import cache
from fastapi_pagination import Page, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from app.blog.schemas import (PostCreate, ShowPost, UpdatedPostResponse,
                              UpdatePostRequest)
from app.blog.services import (_create_post, _delete_post, _get_all_posts,
                               _get_post_by_id, _get_post_by_slug,
                               _get_post_by_title, _get_posts_by_user_id,
                               _update_post)
from app.user import security
from app.user.models import User
from app.user.services import _check_user_permissions, _get_user_by_id
from db.session import get_db

post_router = APIRouter(
    prefix='/posts',
)


@post_router.get("/", response_model=ShowPost, tags=['Posts'])
async def get_post(post_id: int = None,
                   post_title: str = None,
                   post_slug: str = None,
                   db_session: AsyncSession = Depends(get_db)) -> ShowPost:
    if post_id:
        post = await _get_post_by_id(post_id, db_session)
    elif post_slug:
        post = await _get_post_by_slug(post_slug, db_session)
    elif post_title:
        post = await _get_post_by_title(post_title, db_session)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not enough data."
        )
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )
    return post


@post_router.get("/user_id", response_model=Page[ShowPost], tags=['Posts'])
async def get_posts_by_user_id(user_id: int,
                               db_session: AsyncSession = Depends(get_db)) -> \
        Page[ShowPost]:
    user_posts = await _get_posts_by_user_id(user_id, db_session)
    return paginate(user_posts)


@post_router.get("/list", response_model=Page[ShowPost], tags=['Posts'])
@cache(expire=60)
async def get_all_posts(db_session: AsyncSession = Depends(get_db)) \
        -> Page[ShowPost]:
    list_posts = await _get_all_posts(db_session)
    return paginate(list_posts)


@post_router.post("/", response_model=ShowPost, tags=['Posts'])
async def create_post(post: PostCreate,
                      db_session: AsyncSession = Depends(get_db),
                      current_user: User = Depends(
                          security.get_current_user_from_token)) -> ShowPost:
    return await _create_post(post, db_session, current_user)


@post_router.patch("/", response_model=UpdatedPostResponse, tags=['Posts'])
async def update_post_by_id(post_id: int,
                            data_to_update: UpdatePostRequest,
                            db_session: AsyncSession = Depends(get_db),
                            current_user:
                            User =
                            Depends(security.get_current_user_from_token)) \
        -> UpdatedPostResponse:
    updated_post_params = data_to_update.model_dump(exclude_none=True)
    if updated_post_params == {}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("At least one parameter for post update "
                    "info should be provided"),
        )
    post = await _get_post_by_id(post_id, db_session)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found."
        )
    author_id = post.author_id
    if author_id != current_user.id:
        user_author = await _get_user_by_id(author_id, db_session)
        if not _check_user_permissions(target_user=user_author,
                                       current_user=current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden. Not enough rights.")
    updated_post = await _update_post(post_id, updated_post_params, db_session)
    return updated_post


@post_router.delete("/", status_code=status.HTTP_200_OK,
                    tags=['Posts'])
async def delete_post(
        post_id: int,
        db_session: AsyncSession = Depends(get_db),
        current_user: User = Depends(security.get_current_user_from_token)) \
        -> Response:
    post = await _get_post_by_id(post_id, db_session)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    if post.author_id != current_user.id:
        user_author = await _get_user_by_id(post.author_id, db_session)
        if not _check_user_permissions(target_user=user_author,
                                       current_user=current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden. Not enough rights.")
    await _delete_post(post_id, db_session)
    return Response(status_code=status.HTTP_200_OK)
