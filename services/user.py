from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User
from fastapi import HTTPException
from services.hash import HashService
from core.logger import logger

class UserService:
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(email: str, password: str, db: AsyncSession) -> User:
        if await UserService.get_user_by_email(email, db):
            logger.error('User already exists with same email')
            raise HTTPException(status_code=400, detail="Email already exists")
        
        db_user = User(email=email, hashed_password=HashService.get_password_hash(password))
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info('User created successfully.')
        return db_user