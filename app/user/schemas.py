from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        from_attributes = True


class ShowUser(TunedModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    is_superuser: bool


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    def validate_username(cls: Any, username: str, **kwargs: Any) -> Any:
        if len(username) <= 4:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Username must be more than 4 characters")
        return username

    @field_validator("email")
    def validate_email(cls: Any, email: str, **kwargs: Any) -> Any:
        if len(email) == 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="An email is required")
        return email


class UpdateUserRequest(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None

    @field_validator("username")
    def validate_username(cls, username: str):
        if len(username) <= 4:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Username must be more than 4 characters")
        return username

    @field_validator("email")
    def validate_email(cls, email: str):
        if len(email) == 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="An email is required")
        return email


class UpdatedUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class DeleteUserResponse(BaseModel):
    deleted_user_id: int
