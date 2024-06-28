from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class PostCreate(BaseModel):
    title: str
    text: str
    short_description: str

    @field_validator("title")
    def validate_title(cls, title: str):
        if len(title) == 0:
            raise ValueError("Title can't be empty")
        elif len(title) > 100:
            raise ValueError("Title is too long")
        return title

    @field_validator("short_description")
    def validate_short_description(cls, short_description: str):
        if len(short_description) == 0:
            raise ValueError("Short description can't be empty")
        elif len(short_description) > 200:
            raise ValueError("Short description is too long")
        return short_description

    @field_validator("text")
    def validate_text(cls, text: str):
        if len(text) == 0:
            raise ValueError("Text can't be empty")
        return text


class ShowPost(BaseModel):
    id: int
    author_id: int
    title: str
    text: str
    short_description: str
    slug: str
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdatePostRequest(BaseModel):
    title: str = None
    text: str = None
    short_description: str = None


class UpdatedPostResponse(BaseModel):
    id: int
    title: str
    text: str
    short_description: str

    model_config = ConfigDict(from_attributes=True)


class PostServiceResult(BaseModel):
    success: bool
    status_code: int
    detail: str = None
    data: Any = None
