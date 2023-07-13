from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator




class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        orm_mode = True


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
            raise HTTPException(status_code=422, detail="Username must be more than 4 characters")
        return username

    @field_validator("email")
    def validate_email(cls: Any, email: str, **kwargs: Any) -> Any:
        if len(email) == 0:
            raise HTTPException(status_code=422, detail="An email is required")
        return email

