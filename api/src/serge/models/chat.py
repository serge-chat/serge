from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from datetime import datetime
from langchain.llms import LlamaCpp
from langchain.memory import RedisChatMessageHistory

class Chat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)

    llm: LlamaCpp