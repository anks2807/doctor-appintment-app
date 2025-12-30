from enum import Enum

class UserRole(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"