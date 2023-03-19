from beanie import Document, Link
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import Field

from datetime import datetime


class ChatParameters(Document):
    model: str = Field(default="ggml-alpaca-13b-q4.bin")
    temperature: float = Field(default=0.1)

    top_k: int = Field(default=50)
    top_p: float = Field(default=0.95)

    max_length: int = Field(default=256)

    repeat_last_n: int = Field(default=64)
    repeat_penalty: float = Field(default=1.3)


class Question(Document):
    question: str
    answer: str


class Chat(Document):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
    questions: Optional[List[Link[Question]]]
    parameters: Link[ChatParameters]


class LastModelUsed(Document):
    name: str
