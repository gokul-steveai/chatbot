from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from core.config import settings
from core.logger import logger

class TokenService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        payload = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        
        payload.update({"exp": expire})
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        logger.info('Access token generated successfully.')
        
        return token

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            logger.error('Invalid JWT token.')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )