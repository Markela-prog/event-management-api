from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_orm = True
        from_attributes = True


class UpdateUserProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class User(UserBase):
    id: int

    class Config:
        from_orm = True