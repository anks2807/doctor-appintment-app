from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.roles import Role
from app.models.availability import AvailabilityOut


class UserCreateDto(BaseModel):
    email: EmailStr
    password: str
    role: Role


class UserDto(BaseModel):
    id: int
    email: EmailStr
    role: Role

    model_config = ConfigDict(from_attributes=True)


class DoctorOut(UserDto):
    availabilities: List[AvailabilityOut] = []
