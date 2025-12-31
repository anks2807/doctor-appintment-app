from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator
import datetime


class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class AvailabilityBase(BaseModel):
    day_of_week: DayOfWeek
    start_time: datetime.time
    end_time: datetime.time

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def parse_time(cls, value: str) -> datetime.time:
        """
        Allow parsing of time in both 12-hour (e.g., "01:00:00PM")
        and 24-hour (e.g., "13:00:00") formats.
        """
        if isinstance(value, str):
            try:
                return datetime.datetime.strptime(value.upper(), "%I:%M:%S%p").time()
            except ValueError:
                pass
        return value


class AvailabilityOut(AvailabilityBase):
    id: int
    doctor_id: int
    model_config = ConfigDict(from_attributes=True)