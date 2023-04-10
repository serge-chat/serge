from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from datetime import datetime
from serge.utils.llm import LlamaCpp
from langchain.memory import RedisChatMessageHistory

class Chat(BaseModel):
    id: str = Field(default_factory=lambda:str(uuid4()))
    created: datetime = Field(default_factory=datetime.now)

    llm: LlamaCpp