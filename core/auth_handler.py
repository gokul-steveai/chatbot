from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from db.connect import get_db
from db.models import User
from services.hash import security
from services.token import TokenService
from services.user import UserService
from core.logger import logger

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    token = credentials.credentials
    payload = TokenService.decode_token(token)
    email: str = payload.get("sub")

    if email is None:
        logger.warning('Invalid access token')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = await UserService.get_user_by_email(email, db)
    
    if user is None:
        logger.warning('Invalid user details in the token')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user