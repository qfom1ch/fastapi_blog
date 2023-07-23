from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class ShowUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    def validate_username(cls, username: str):
        if len(username) <= 4:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username must be more than 4 characters")
        return username


class UpdateUserRequest(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None

    @field_validator("username")
    def validate_username(cls, username: str):
        if len(username) <= 4:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username must be more than 4 characters")
        return username

    @field_validator("email")
    def validate_email(cls, email: str):
        if len(email) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="An email is required")
        return email


class UpdatedUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class DeleteUserResponse(BaseModel):
    deleted_user_id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
