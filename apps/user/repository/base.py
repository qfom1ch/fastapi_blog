from abc import ABC, abstractmethod
from typing import Sequence

from apps.user.models import User
from apps.user.schemas import UserCreate


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: UserCreate) -> User:
        ...

    @abstractmethod
    async def get_user(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        ...

    @abstractmethod
    async def get_all(self) -> Sequence[User]:
        ...

    @abstractmethod
    async def update(self, user_id: int, updated_user_params: dict) -> User | None:
        ...

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        ...

    @abstractmethod
    async def check_duplicate_email(self, email: str) -> bool:
        ...

    @abstractmethod
    async def check_duplicate_username(self, username: str) -> bool:
        ...
