
from sqlalchemy import Column, Integer, Enum, String
from sqlalchemy.orm import relationship

from app.util.roles import UserRole
from app.db.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name = 'user_role_enum'), nullable=False)

    doctor = relationship("Doctor", back_populates="user", uselist=False)
    patient = relationship("Patient", back_populates="user", uselist=False)