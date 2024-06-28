from fastapi import status

from apps.post.schemas import PostCreate, PostServiceResult, UpdatePostRequest
from apps.user.models import User

from ..user import security
from .models import Post
from .repository.base import PostRepository


class PostService:
    def __init__(self, post_repository: PostRepository):
        self._post_repository = post_repository

    async def create(self, post: PostCreate, current_user: User) -> PostServiceResult:
        new_post = await self._post_repository.create(post=post, current_user=current_user)
        return PostServiceResult(success=True, status_code=status.HTTP_200_OK, data=new_post)

    async def get_post(self, post_id: int) -> PostServiceResult:
        post = await self._post_repository.get_post(post_id=post_id)
        if not post:
            return PostServiceResult(
                success=False, status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.",
            )

        return PostServiceResult(success=True, status_code=status.HTTP_200_OK, data=post)

    async def get_by_user_id(self, user_id: int) -> PostServiceResult:
        user_posts = await self._post_repository.get_by_user_id(user_id=user_id)
        return PostServiceResult(success=True, status_code=status.HTTP_200_OK, data=user_posts)

    async def get_all(self) -> PostServiceResult:
        posts = await self._post_repository.get_all()
        return PostServiceResult(success=True, status_code=status.HTTP_200_OK, data=posts)

    async def update(self, post_id: int, data_to_update: UpdatePostRequest, current_user: User) -> PostServiceResult:
        updated_post_params = data_to_update.model_dump(exclude_none=True)

        if not updated_post_params:
            return PostServiceResult(
                success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one parameter for user update info should be provided",
            )

        post = await self._get_post_or_404(post_id=post_id)
        if isinstance(post, PostServiceResult):
            return post

        if post.author_id != current_user.id:
            if not security.check_user_permissions(target_user=post.author, current_user=current_user):
                return PostServiceResult(
                    success=False, status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden.",
                )

        updated_post = await self._post_repository.update(
            post_id=post_id, updated_post_params=updated_post_params
        )

        return PostServiceResult(success=True, status_code=status.HTTP_200_OK, data=updated_post)

    async def delete(self, post_id: int, current_user: User) -> PostServiceResult:
        post = await self._get_post_or_404(post_id=post_id)
        if isinstance(post, PostServiceResult):
            return post

        if post.author_id != current_user.id:
            if not security.check_user_permissions(target_user=post.author, current_user=current_user):
                return PostServiceResult(
                    success=False, status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden.",
                )

        await self._post_repository.delete(post_id=post_id)

        return PostServiceResult(success=True, status_code=status.HTTP_204_NO_CONTENT)

    async def _get_post_or_404(self, post_id: int) -> Post | PostServiceResult:
        post = await self._post_repository.get_post(post_id=post_id)
        if not post:
            return PostServiceResult(
                success=False, status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
            )
        return post
