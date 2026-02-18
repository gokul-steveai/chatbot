from fastapi import APIRouter, Depends, Response, status
from schema.models import ChatHistory, QueryRequest, QueryResponse, ApiResponse
from db.models import User
from services.chat import ChatService
from services.prompt import PromptService
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.rag import get_rag_pipeline
from core.auth_handler import get_current_user
from db.connect import get_db
from rag import RAGPipeline

user_router = APIRouter(prefix="/users", tags=["Users API"])

@user_router.get('/history', response_model=ApiResponse[list[ChatHistory]], response_model_exclude_none=True)
async def get_history(
        page: int = 1, 
        limit:int = 20, 
        current_user: User = Depends(get_current_user), 
        db: AsyncSession = Depends(get_db)
    ) -> ApiResponse[list[ChatHistory]]:
    
    chat_history = await ChatService.get_user_history(current_user.id, db, page, limit)
    return ApiResponse(data=chat_history)


@user_router.post('/query', response_model=ApiResponse[QueryResponse], response_model_exclude_none=True)
async def query_response(
        body: QueryRequest, 
        response: Response,
        current_user: User = Depends(get_current_user), 
        db: AsyncSession = Depends(get_db), 
        rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)
    ) -> ApiResponse[QueryResponse]:
    
    prompt = await PromptService.prepare_prompt_with_history(body.query, current_user.id, db)
    
    try: 
        response = await rag_pipeline.query(prompt)
        await ChatService.save_chat(current_user.id, body.query, response, db)
    except Exception as e:
        print(f"Error during query: {e}")
        response = "Sorry, I couldn't process your request at the moment."
        response.status_code = status.HTTP_400_BAD_REQUEST
        
        return ApiResponse(error= response, code=status.HTTP_400_BAD_REQUEST)
    
    return ApiResponse(data= QueryResponse(response=response), message="Success")

    