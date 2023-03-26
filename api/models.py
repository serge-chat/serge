from beanie import Document, Link
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import Field

from datetime import datetime
from enum import Enum

class ChatParameters(Document):
    model: str = Field(default="ggml-alpaca-7B-q4_0.bin")
    temperature: float = Field(default=0.1)

    top_k: int = Field(default=50)
    top_p: float = Field(default=0.95)

    max_length: int = Field(default=256)
    context_window: int = Field(default=512)

    repeat_last_n: int = Field(default=64)
    repeat_penalty: float = Field(default=1.3)

    init_prompt: str = Field(default="")
    
    n_threads: int = Field(default=4)

class Question(Document):
    question: str
    answer: Optional[str]
    error: Optional[str]



class Chat(Document):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
    questions: Optional[List[Link[Question]]]
    parameters: Link[ChatParameters]
