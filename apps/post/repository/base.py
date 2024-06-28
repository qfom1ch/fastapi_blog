from abc import ABC, abstractmethod
from typing import Sequence

from apps.post.models import Post
from apps.post.schemas import PostCreate
from apps.user.models import User


class PostRepository(ABC):
    @abstractmethod
    async def create(self, post: PostCreate, current_user: User) -> Post:
        ...

    @abstractmethod
    async def get_post(self, post_id: int) -> Post | None:
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Sequence[Post]:
        ...

    @abstractmethod
    async def get_all(self) -> Sequence[Post]:
        ...

    @abstractmethod
    async def update(self, post_id: int, updated_post_params: dict) -> Post | None:
        ...

    @abstractmethod
    async def delete(self, post_id: int) -> None:
        ...
