from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str|None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    moderator = "moderator"


class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        from_attribute = True


class RoleChangeRequest(BaseModel):
    user_id: int
    new_role: UserRole


class UserUpdate(BaseModel):
    username: str
    email: str
    avatar: str


class PostCommentReques(BaseModel):
    image_id: int
    text: str


class GetCommentResponce(BaseModel):
    id: int
    text: str
    created_at: datetime
    updated_at: datetime | None
    image_id: int
    user_id: int


class PutCommentReques(BaseModel):
    comment_id: int
    new_text: str


class RatingCreate(BaseModel):
    image_id: int
    rating: int = Field(gt=0, le=5)


class RatingResponse(BaseModel):
    id: int
    rating: int
    user_id: int
    image_id: int

    class Config:
        from_attributes = True


class ImageResponce(BaseModel):
    id: int
    description: str
    image_url: str
    author_id: int
    qr_code_url: str
    created_dt: datetime


class CropImageRequest(BaseModel):
    image_id: int
    width: int
    height: int
    description: str


class RoundCornersImageRequest(BaseModel):
    image_id: int
    radius: int
    description: str


class EffectImageRequest(BaseModel):
    image_id: int
    description: str

class FirstAdminModel(UserModel):
    id: int = 1
    role: UserRole = UserRole.admin
    password: str
