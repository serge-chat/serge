from os import getenv
from pydantic import BaseSettings

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:////data/db/sql_app.db"
    NODE_ENV: str = "development"

    def __init__(self):
        db_url = getenv("SQLALCHEMY_DATABASE_URL", None)
        if db_url:
            self.SQLALCHEMY_DATABASE_URL = db_url
        super(Settings, self).__init__()

    class Config:
        orm_mode = True
