from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    moderator = "moderator"

class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        orm_mode = True