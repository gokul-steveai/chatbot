from fastapi import APIRouter, Depends
from models import UserRegister, UserLogin, Token
from sqlalchemy.ext.asyncio import AsyncSession
from db.connect import get_db
from services import UserService

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])

@auth_router.post('/register', response_model=Token, status_code=201)
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    await UserService.create_user(user.email, user.password, db)
    access_token = UserService.generate_token(user.email)
    return Token(access_token=access_token)

@auth_router.post('/login', response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    await UserService.authenticate_user(user.email, user.password, db)
    access_token = UserService.generate_token(user.email)
    return Token(access_token=access_token)