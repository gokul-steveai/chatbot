from fastapi import APIRouter, Depends, status
from schema.models import UserRegister, UserLogin, Token, ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db.connect import get_db
from services.user import UserService
from services.auth import AuthService

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])

@auth_router.post('/register', response_model=ApiResponse[Token], status_code=201, response_model_exclude_none=True)
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)) -> ApiResponse[Token]:
    await UserService.create_user(user.email, user.password, db)
    access_token = AuthService.generate_token(user.email)
    return ApiResponse(data=Token(access_token=access_token), message="User created successfully.", code=status.HTTP_201_CREATED)

@auth_router.post('/login', response_model=ApiResponse[Token], response_model_exclude_none=True)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)) -> ApiResponse[Token]:
    await AuthService.authenticate_user(user.email, user.password, db)
    access_token = AuthService.generate_token(user.email)
    return ApiResponse(data= Token(access_token=access_token), message="Login successfully")