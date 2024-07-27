from os import getenv

from pydantic import BaseSettings


class Settings(BaseSettings):
    SERGE_DATABASE_URL: str = getenv("SERGE_DATABASE_URL", "sqlite:////data/db/sql_app.db")
    NODE_ENV: str = "development"
    SERGE_JWT_SECRET: str = getenv("SERGE_JWT_SECRET", "uF7FGN5uzfGdFiPzR")
    SERGE_SESSION_EXPIRY: int = getenv("SERGE_SESSION_EXPIRY", 60)

    class Config:
        orm_mode = True
