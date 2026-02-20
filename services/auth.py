from services.user import UserService
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from core.config import settings
from datetime import timedelta
from services.hash import HashService
from services.token import TokenService
from core.logger import logger

class AuthService:
    @staticmethod
    async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
        user = await UserService.get_user_by_email(email, db)
        if not user or not HashService.verify_password(password, user.hashed_password):
            logger.warning('Invalid login credentials')
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    
    @staticmethod
    def generate_token(email: str) -> str:
        return TokenService.create_access_token(
            data={"sub": email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )