from sqlalchemy.ext.asyncio import AsyncSession
from services.chat import ChatService

class PromptService:
    @staticmethod
    async def prepare_prompt_with_history(prompt: str, user_id: int, db: AsyncSession) -> str:
        # Fetch recent chat history for context
        chats = await ChatService.get_recent_history(user_id, db, 3)
        
        print(f'{len(chats)} records fetched from chat history.')
        
        if chats:
            previous_conversations = "".join(
                f"Q: {chat.query}. A: {chat.response}\n"
                for chat in chats
            )
            
            return (f"""======== Previous conversations(History) =====
                {previous_conversations}
                
                ===== Current Request ===== 
                {prompt}
            """)
        else:
            return prompt