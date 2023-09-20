from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class ChatParameters(BaseModel):
    model_path: str
    n_ctx: int
    n_gpu_layers: int
    # n_parts: int
    # seed: int
    # f16_kv: bool
    # logits_all: bool
    # vocab_only: bool
    # use_mlock: bool
    n_threads: int
    # n_batch: int
    last_n_tokens_size: int
    max_tokens: int
    temperature: float
    top_p: float
    # logprobs: int
    # echo: bool
    # stop_sequences: list
    repeat_penalty: float
    top_k: int
    # stream: bool
    init_prompt: str | None = "Below is an instruction that describes a task. Write a response that appropriately completes the request."


class Chat(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created: datetime = Field(default_factory=datetime.now)

    params: ChatParameters
