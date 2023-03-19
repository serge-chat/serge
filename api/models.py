from beanie import Document, Link
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import Field

from datetime import datetime


class Question(Document):
    question: str
    answer: str


class Chat(Document):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
    questions: Optional[List[Link[Question]]]


class LastModelUsed(Document):
    name: str
