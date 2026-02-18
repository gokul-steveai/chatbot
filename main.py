from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteException
from contextlib import asynccontextmanager
from db.connect import engine, Base
from rag import RAGPipeline
from routers.auth import auth_router
from routers.user import user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    app.state.rag_pipeline = await RAGPipeline().initialize()
    yield
    
app = FastAPI(title='Chatbot', lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
    

@app.exception_handler(StarletteException)
async def global_exception_handler(request: Request, exc: StarletteException):
    print(f'Inside global exception handler: Details: {exc.detail}')
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc.detail)
        }
    )