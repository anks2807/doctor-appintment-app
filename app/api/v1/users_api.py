from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.login_dto import LoginDto
from app.models.token import Token
from app.models.users import UserDto
from app.schema.users import User as UserModel
from app.core.security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/auth/register", response_model=UserDto, status_code=status.HTTP_201_CREATED)
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


@router.post('/auth/login', response_model=Token)
def login(login_dto: LoginDto, db: Session=Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == login_dto.email).first()

    if not db_user:
        # Use a generic error message to avoid revealing if a user exists
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    if not verify_password(login_dto.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    # Create a dictionary with the claims for the JWT
    token_data = {"sub": db_user.email, "role": db_user.role.value}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}