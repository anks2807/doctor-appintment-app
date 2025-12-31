from sqlalchemy import Column, Integer, ForeignKey, Enum, Time
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.availability import DayOfWeek


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    doctor = relationship("User", back_populates="availabilities")