from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    NODE_ENV: str = "development"

    class Config:
        orm_mode = True
