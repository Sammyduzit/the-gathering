from fastapi import  APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta

from app.core.database import get_db
from app.models import User
from app.schemas.auth_schemas import UserResponse, UserRegister, UserLogin
from app.core.auth_utils import hash_password, verify_password
from app.core.jwt_utils import create_access_token
from app.core.auth_dependencies import get_current_active_user
from app.core.config import settings
from app.schemas.auth_schemas import Token

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    :param user_data: New user data
    :param db: Database session
    :return: Created user object
    """
    existing_email_query = select(User).where(User.email == user_data.email)
    result = db.execute(existing_email_query)
    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username_query = select(User).where(User.username == user_data.username)
    result = db.execute(existing_username_query)
    existing_username = result.scalar_one_or_none()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        email= user_data.email,
        username= user_data.username,
        password_hash= hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.
    :param user_credentials: User login credentials
    :param db: Database session
    :return: JWT token object
    """
    select_user = select(User).where(User.email == user_credentials.email)
    result = db.execute(select_user)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data = {"sub": user.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user info.
    :param current_user: Current authenticated user
    :return: User information
    """
    return current_user