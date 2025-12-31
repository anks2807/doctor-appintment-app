
from sqlalchemy import Column, Integer, Enum, String
from sqlalchemy.orm import relationship

from app.models.roles import Role
from app.db.base_class import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False)

    availabilities = relationship("Availability", back_populates="doctor", cascade="all, delete-orphan")
    appointments_as_doctor = relationship("Appointment", foreign_keys="[Appointment.doctor_id]", back_populates="doctor", cascade="all, delete-orphan")
    appointments_as_patient = relationship("Appointment", foreign_keys="[Appointment.patient_id]", back_populates="patient", cascade="all, delete-orphan")