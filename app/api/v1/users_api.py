from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.login_dto import LoginDto
from app.models.token import Token
from app.models.password import ForgotPasswordRequest, ResetPasswordRequest
from app.models.users import UserDto, UserCreateDto
from app.schema.users import User as UserModel
from app.core.security import create_access_token, hash_password, verify_password, create_password_reset_token, verify_password_reset_token

router = APIRouter()


@router.post("/auth/register", response_model=UserDto, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreateDto, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    if not verify_password(login_dto.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token_data = {"sub": db_user.email, "role": db_user.role.value}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Forgot password endpoint. In this mock flow, it returns the reset token.
    In a real application, this would send an email and return a success message.
    """
    user = db.query(UserModel).filter(UserModel.email == request.email).first()
    # To prevent user enumeration, we don't reveal if the user was found.
    # We proceed as if the process was successful.
    if user:
        password_reset_token = create_password_reset_token(email=request.email)
        # In a real app, you would email this token. Here, we return it.
        return {"msg": "Password reset token generated.", "reset_token": password_reset_token}
    
    return {"msg": "If an account with this email exists, a password reset link has been sent."}


@router.post("/auth/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset user password using a valid token.
    """
    email = verify_password_reset_token(token=request.token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password = hash_password(request.new_password)
    db.commit()

    return {"msg": "Password has been reset successfully."}