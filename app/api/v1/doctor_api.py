from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.v1.auth import get_current_doctor
from app.models.availability import AvailabilityBase, AvailabilityOut
from app.schema.availability import Availability as AvailabilityModel
from app.schema.users import User as UserModel

router = APIRouter()


@router.post(
    "/availability",
    response_model=List[AvailabilityOut],
    status_code=status.HTTP_201_CREATED,
)
def set_doctor_availability(
    availabilities: List[AvailabilityBase],
    db: Session = Depends(get_db),
    current_doctor: UserModel = Depends(get_current_doctor),
):
    """
    Set or update the weekly availability for the logged-in doctor.
    This will replace any existing availability for the doctor.
    """
    # Clear old availability
    current_doctor.availabilities = []

    # Add new availability
    for item in availabilities:
        db_availability = AvailabilityModel(**item.model_dump(), doctor_id=current_doctor.id)
        current_doctor.availabilities.append(db_availability)

    db.add(current_doctor)
    db.commit()
    db.refresh(current_doctor)

    return current_doctor.availabilities