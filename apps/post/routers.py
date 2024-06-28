from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi_cache.decorator import cache
from fastapi_pagination import Page, paginate

import apps.user.depends
from apps.post.schemas import (PostCreate, PostServiceResult, ShowPost,
                               UpdatedPostResponse, UpdatePostRequest)
from apps.user.models import User

from .depends import get_post_service_sqlalchemy
from .service import PostService

post_router = APIRouter(
    prefix='/posts',
)


@post_router.get("/", response_model=ShowPost, tags=['Posts'])
async def get_post(post_id: int, post_service: PostService = Depends(get_post_service_sqlalchemy)) -> ShowPost:
    post_result: PostServiceResult = await post_service.get_post(post_id=post_id)

    if not post_result.success:
        raise HTTPException(
            status_code=post_result.status_code,
            detail=post_result.detail,
        )

    return post_result.data


@post_router.get("/user_id", response_model=Page[ShowPost], tags=['Posts'])
async def get_posts_by_user_id(
        user_id: int, post_service: PostService = Depends(get_post_service_sqlalchemy),
) -> Page[ShowPost]:
    user_posts: PostServiceResult = await post_service.get_by_user_id(user_id=user_id)
    return paginate(user_posts.data)


@post_router.get("/list", response_model=Page[ShowPost], tags=['Posts'])
@cache(expire=60)
async def get_all(post_service: PostService = Depends(get_post_service_sqlalchemy)) -> Page[ShowPost]:
    result_posts: PostServiceResult = await post_service.get_all()
    return paginate(result_posts.data)


@post_router.post("/", response_model=ShowPost, tags=['Posts'])
async def create(
        post: PostCreate,
        post_service: PostService = Depends(get_post_service_sqlalchemy),
        current_user: User = Depends(apps.user.depends.get_current_user_from_token),
) -> ShowPost:
    create_result: PostServiceResult = await post_service.create(post=post, current_user=current_user)
    return create_result.data


@post_router.patch("/", response_model=UpdatedPostResponse, tags=['Posts'])
async def update(
        post_id: int,
        data_to_update: UpdatePostRequest,
        current_user: User = Depends(apps.user.depends.get_current_user_from_token),
        post_service: PostService = Depends(get_post_service_sqlalchemy),
) -> UpdatedPostResponse:

    update_result: PostServiceResult = await post_service.update(
        post_id=post_id, data_to_update=data_to_update, current_user=current_user,
    )

    if not update_result.success:
        raise HTTPException(
            status_code=update_result.status_code,
            detail=update_result.detail,
        )

    return update_result.data


@post_router.delete("/", status_code=status.HTTP_204_NO_CONTENT, tags=['Posts'])
async def delete(
        post_id: int,
        current_user: User = Depends(apps.user.depends.get_current_user_from_token),
        post_service: PostService = Depends(get_post_service_sqlalchemy),
) -> Response:
    delete_result: PostServiceResult = await post_service.delete(post_id=post_id, current_user=current_user)

    if not delete_result.success:
        raise HTTPException(
            status_code=delete_result.status_code,
            detail=delete_result.detail,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
