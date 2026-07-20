from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='../.env', 
        env_file_encoding='utf-8',
        extra='ignore'
    )

    DATABASE_URL: str
    TEST_DATABASE_URL: str
    REDIS_URL: str
    CACHE_TTL_SECONDS: int
    CACHE_TASKS_KEY: str
    CACHE_CATEGORIES_KEY: str
    CORS_ALLOWED_ORIGINS: list[str]

@lru_cache
def get_settings() -> Settings:
    return Settings()