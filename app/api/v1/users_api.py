from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.users import UserDto
from app.schema.users import User as UserModel
from app.core.security import hash_password

router = APIRouter()


@router.post("/users", response_model=UserDto, status_code=status.HTTP_201_CREATED)
def register_user(user: UserDto, db: Session = Depends(get_db)):
    """
    Register a new user (Doctor or Patient).
    """
    db_user = UserModel(
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user