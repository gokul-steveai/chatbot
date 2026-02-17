from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.models import User, ChatSession
from utils import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from config import settings
from fastapi import HTTPException

class UserService:
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(email: str, password: str, db: AsyncSession) -> User:
        if await UserService.get_user_by_email(email, db):
            raise HTTPException(status_code=400, detail="Email already exists")
        
        db_user = User(email=email, hashed_password=get_password_hash(password))
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
        user = await UserService.get_user_by_email(email, db)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    
    @staticmethod
    def generate_token(email: str) -> str:
        return create_access_token(
            data={"sub": email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )

class ChatService:
    @staticmethod
    async def save_chat(user_id: int, query: str, response: str, db: AsyncSession) -> ChatSession:
        chat_session = ChatSession(user_id=user_id, query=query, response=response)
        db.add(chat_session)
        await db.commit()
        await db.refresh(chat_session)
        return chat_session
    
    @staticmethod
    async def get_user_history(user_id: int, db: AsyncSession, page: int = 1, limit: int = 20) -> list[ChatSession]:
        result = await db.execute(
            select(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .offset((page - 1)* limit).limit(limit)
            .order_by(desc(ChatSession.created_at), desc(ChatSession.id))
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_recent_history(user_id: int, db: AsyncSession, limit: int = 3) -> list[ChatSession]:
        result = await db.execute(
            select(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.created_at), desc(ChatSession.id))
            .limit(limit)
        )
        return result.scalars().all()
