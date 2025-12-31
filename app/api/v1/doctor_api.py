from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.v1.auth import get_current_doctor
from app.schema.users import User as UserModel
from app.models.roles import Role
from app.models.users import UserDto

router = APIRouter()


@router.get(path="/doctors", response_model=List[UserDto])
def get_doctors(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_doctor)):
    all_doctors = db.query(UserModel).filter(UserModel.role == Role.DOCTOR).all()

    if not all_doctors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Doctors Found")

    return all_doctors
