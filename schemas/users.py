from pydantic import BaseModel
from schemas.msgs import Msg



class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str



class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    level:str
    max_usage: int
    current_usage:int
    items: list[Msg] = []

    class Config:
        from_attributes = True

    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
