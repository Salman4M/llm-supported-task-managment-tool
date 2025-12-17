from core.config import settings
from typing import Union,Any
from datetime import datetime,timezone,timedelta
from jose import jwt
from passlib.context import CryptContext
# import redis.asyncio as redis
from cachetools import TTLCache

# redis_client = redis.Redis(
#     host=settings.REDIS_HOST, 
#     port=settings.REDIS_PORT, 
#     decode_responses=True
# )

BLACKLISTED_TOKENS = TTLCache(maxsize=10000, ttl=8*24*60*60)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password: str , hashed_password: str):
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_token(subject: Union[str, Any], expires_delta: timedelta, type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": type}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: Any) -> str:
    return create_token(subject, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access")

def create_refresh_token(subject: Any) -> str:
    return create_token(subject, timedelta(days=settings.REFRESH_TOKEN_LIFETIME_DAYS), "refresh")


# --- Blocklist Logic ---
async def add_to_blacklist(token: str, expires_in: int = None):
    BLACKLISTED_TOKENS[token] = True

async def is_token_blacklisted(token: str) -> bool:
    return token in BLACKLISTED_TOKENS

def clear_blacklist():
    BLACKLISTED_TOKENS.clear()

def get_bloclisted_size():
    return len(BLACKLISTED_TOKENS)
    