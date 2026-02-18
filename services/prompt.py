from sqlalchemy.ext.asyncio import AsyncSession
from services.chat import ChatService
from core.logger import logger

class PromptService:
    @staticmethod
    async def prepare_prompt_with_history(prompt: str, user_id: int, db: AsyncSession) -> str:
        # Fetch recent chat history for context
        chats = await ChatService.get_recent_history(user_id, db, 3)
        
        logger.info(f'{len(chats)} records fetched from chat history.')
        
        if chats:
            previous_conversations = "".join(
                f"Q: {chat[0]}. A: {chat[1]}\n"
                for chat in chats
            )
            
            return (f"""
            ======== Previous conversations(History) =====
            {previous_conversations}
                
            ===== Current Request ===== 
            {prompt}
            """)
        else:
            return prompt