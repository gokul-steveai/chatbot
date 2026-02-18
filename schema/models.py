from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import datetime
from typing import Generic, TypeVar, Optional

class QueryRequest(BaseModel):
    query: str = Field(min_length=2)
    
    @field_validator('query')
    def validate_query(cls, q: str):
        if q.strip() == '':
            raise ValueError("query can't be empty") 
        return q
        
class QueryResponse(BaseModel):
    response: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str

class ChatHistory(BaseModel):
    id: int
    query: str
    response: str
    created_at: datetime
    
T = TypeVar('T')
class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=200, example=200)
    message: str = Field(default="success", example="success")
    data: Optional[T]
    error: str | None = None