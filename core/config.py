from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM Task Manager"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    HEADER: str = "Bearer"
    REFRESH_TOKEN_LIFETIME_DAYS: int = 7
    REDIS_PORT: str = "redis_service" or "localhost"
    REDIS_HOST: int = 6379

    class Config:
        env_file = ".env"


settings = Settings()
