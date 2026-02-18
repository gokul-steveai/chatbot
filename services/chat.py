from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.models import ChatSession

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