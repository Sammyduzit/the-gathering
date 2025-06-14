from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.jwt_utils import get_user_from_token
from app.models.user import User


security = HTTPBearer()

async def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract JWT token from Authorization header.
    :param credentials: HTTP authorization credentials
    :return: JWT token string
    """
    return credentials.credentials

async def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user from JWT token.
    :param token: JWT token string
    :param db: Database session
    :return: Current user object
    """
    username = get_user_from_token(token)

    select_user = select(User).where(User.username == username)
    result = db.execute(select_user)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User '{username}' not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user.
    :param current_user: Current user from token
    :return: Active user object
    """
    return current_user


async def get_current_admin_user():
    pass