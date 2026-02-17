from fastapi import APIRouter, Depends
from models import ChatHistory
from db.models import User
from services import ChatService
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_current_user
from db.connect import get_db

user_router = APIRouter(prefix="/users", tags=["Users API"])

@user_router.get('/history', response_model=list[ChatHistory])
async def get_history(page: int = 1, limit:int = 20, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await ChatService.get_user_history(current_user.id, db, page, limit)
    