from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator
import datetime

from app.models.users import UserDto


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_time: datetime.datetime

    @field_validator("appointment_time", mode="before")
    @classmethod
    def parse_datetime(cls, value: str) -> datetime.datetime:
        """
        Allow parsing of datetime in 12-hour (e.g., "2024-01-01 01:00:00PM")
        and 24-hour/ISO formats.
        """
        if isinstance(value, str):
            try:
                # Attempt to parse 12-hour format with AM/PM
                return datetime.datetime.strptime(value.upper(), "%Y-%m-%d %I:%M:%S %p")
            except ValueError:
                # If it fails, Pydantic's default parser will handle other formats
                pass
        return value


class AppointmentOut(BaseModel):
    id: int
    appointment_time: datetime.datetime
    status: AppointmentStatus
    doctor: UserDto
    patient: UserDto

    model_config = ConfigDict(from_attributes=True)