from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.config import settings
from app.schema.users import User as UserModel
from app.util.roles import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class TokenData(BaseModel):
    sub: str
    role: UserRole


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(**payload)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = db.query(UserModel).filter(UserModel.email == token_data.sub).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_doctor(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user is not a doctor")
    return current_user

def get_current_patient(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user is not a patient")
    return current_user
