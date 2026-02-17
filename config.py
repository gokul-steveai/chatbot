from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    chroma_dir: str = "chroma_db"
    gemini_model: str = "gemini-2.5-flash"
    gemini_api_key: str = 'gemini-secret-key'
    
    database_url: str = "postgresql://user:password@localhost/chatbot_db"
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        
settings = Settings()