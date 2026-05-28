from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str 
    cors_allowed_origins: list[str]


def get_settings() -> Settings: 
    return Settings(
        DATABASE_URL='postgresql+psycopg://user:password@db:5432/todo-db',
        cors_allowed_origins=['http://localhost:3000']
    )