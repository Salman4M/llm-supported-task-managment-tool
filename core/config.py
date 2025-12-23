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
    #ollama config
    OLLAMA_BASE_URL: str
    OLLAMA_MODEL: str
    OLLAMA_TIMEOUT: int
    OLLAMA_API_KEY: str

    # REDIS_PORT: int = 6379
    # REDIS_HOST: str = "localhost"
    # REDIS_HOST: str = "redis_service"


    class Config:
        env_file = ".env"


settings = Settings()
