from typing import Optional

from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

from models import Question, Chat, ChatParameters


class Settings(BaseSettings):
    class Config:
        orm_mode = True


async def initiate_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017/lms")
    await init_beanie(
        database=client.get_default_database(),
        document_models=[Question, Chat, ChatParameters],
    )
