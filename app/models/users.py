from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.roles import Role


class UserCreateDto(BaseModel):
    id: Optional[int]=None
    email: EmailStr
    password: str
    role: Role

class UserDto(BaseModel):
    id: Optional[int]=None
    email: EmailStr
    role: Role

