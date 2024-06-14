from os import getenv

from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = getenv(
        "SQLALCHEMY_DATABASE_URL", "sqlite:////data/db/sql_app.db"
    )
    NODE_ENV: str = "development"
    JWT_SECRET: str = getenv("JWT_SECRET", "uF7FGN5uzfGdFiPzR")
    SESSION_EXPIRY: int = getenv("SESSION_EXPIRY", 60)

    class Config:
        orm_mode = True
