from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.connect import get_db
from db.models import User
from services.hash import security
from services.token import TokenService

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    token = credentials.credentials
    payload = TokenService.decode_token(token)
    email: str = payload.get("sub")

    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user