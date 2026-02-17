from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from db.connect import engine, Base, get_db
from rag import RAGPipeline
from routers.auth import auth_router
from routers.user import user_router
from services import ChatService
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from utils import get_current_user
from models import QueryRequest, QueryResponse

rag_pipeline: RAGPipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    global rag_pipeline
    rag_pipeline = await RAGPipeline().initialize()
    yield
    
app = FastAPI(title='Chatbot', lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)

@app.post('/query', response_model=QueryResponse)
async def query_response(
        request: QueryRequest, 
        current_user: User = Depends(get_current_user), 
        db: AsyncSession = Depends(get_db), 
    ) -> QueryResponse:
    
    prompt = await prepare_prompt_with_history(request.query, current_user.id, db)
    
    try: 
        response = await rag_pipeline.query(prompt)
        await ChatService.save_chat(current_user.id, request.query, response, db)
    except Exception as e:
        print(f"Error during query: {e}")
        response = "Sorry, I couldn't process your request at the moment."
    
    return QueryResponse(response=response)


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