from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from pydantic.types import conint


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

    def __str__(self):
        return f"{self.title} by {self.content}"

    def __repr__(self):
        return f"Post(title={self.title!r}, content={self.content!r})"


class PostCreate(PostBase):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    model_config = ConfigDict(from_attributes=True)


class PostOut(BaseModel):
    Post: Post
    votes: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1, ge=0)  # type: ignore
