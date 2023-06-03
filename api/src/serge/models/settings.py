from pydantic import BaseSettings


class Settings(BaseSettings):
    NODE_ENV: str = "development"

    class Config:
        orm_mode = True
