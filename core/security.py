from core.config import settings
from typing import Union,Any
from datetime import datetime,timezone,timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from requests import Request
from fastapi import HTTPException
import redis.asyncio as redis

redis_client = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    decode_responses=True
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password: str , hashed_password: str):
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_token(subject: Union[str, Any], expires_delta: timedelta, type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": type}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: Any) -> str:
    return create_token(subject, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access")

def create_refresh_token(subject: Any) -> str:
    return create_token(subject, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")


# --- Blocklist Logic ---
async def add_to_blacklist(token: str, expires_in: int = 86400):
    # Store token in Redis with an expiration (so Redis doesn't fill up forever)
    await redis_client.set(f"bl:{token}", "true", ex=expires_in)

async def is_token_blacklisted(token: str) -> bool:
    exists = await redis_client.get(f"bl:{token}")
    return exists is not None
    