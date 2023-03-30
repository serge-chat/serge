# Credit to https://github.com/nsarrazin/serge - this is heavily copied from the API there and not very well yet but it might work.w
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import logging
from datetime import datetime
logger = logging.getLogger(__name__)
import subprocess, os
import asyncio

class ChatParameters(BaseModel):
    model: str = Field(default="ggml-alpaca-13b-q4.bin")
    temperature: float = Field(default=0.2)

    top_k: int = Field(default=50)
    top_p: float = Field(default=0.95)

    max_length: int = Field(default=256)

    repeat_last_n: int = Field(default=64)
    repeat_penalty: float = Field(default=1.3)


class Question(BaseModel):
    question: str
    answer: str


class Chat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
    questions: Optional[List[Question]]
    parameters: ChatParameters


def remove_matching_end(a, b):
    min_length = min(len(a), len(b))

    for i in range(min_length, 0, -1):
        if a[-i:] == b[:i]:
            return b[i:]

    return b


async def generate(
        model: str = "ggml-alpaca-13b-q4.bin",
        prompt: str = "The sky is blue because",
        n_predict: int = 300,
        temp: float = 0.8,
        top_k: int = 10000,
        top_p: float = 0.40,
        repeat_last_n: int = 100,
        repeat_penalty: float = 1.2,
        chunk_size: int = 4,  # Define a chunk size (in bytes) for streaming the output bit by bit
):
    args = (
        "./llama",
        "--model",
        "" + model,
        "--prompt",
        prompt,
        "--n_predict",
        str(n_predict),
        "--temp",
        str(temp),
        "--top_k",
        str(top_k),
        "--top_p",
        str(top_p),
        "--repeat_last_n",
        str(repeat_last_n),
        "--repeat_penalty",
        str(repeat_penalty),
        "--threads",
        "8",
    )
    print(args)
    procLlama = await asyncio.create_subprocess_exec(
        *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    answer = ""

    while True:
        chunk = await procLlama.stdout.read(chunk_size)
        if not chunk:
            return_code = await procLlama.wait()

            if return_code != 0:
                error_output = await procLlama.stderr.read()
                raise ValueError(error_output.decode("utf-8"))
            else:
                return

        chunk = chunk.decode("utf-8")
        print(chunk, end="",flush=True)
        answer += chunk

        if prompt in answer:
            yield remove_matching_end(prompt, chunk)

import asyncio
from langchain.llms.base import LLM, Generation, LLMResult, BaseLLM
from pydantic import BaseModel
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
import threading
from llama_index import SimpleDirectoryReader, LangchainEmbedding, GPTListIndex, PromptHelper
from llama_index import LLMPredictor, ServiceContext
from typing import Optional, List, Mapping, Any

# define prompt helper
# set maximum input size
max_input_size = 2048
# set number of output tokens
num_output = 256
# set maximum chunk overlap
max_chunk_overlap = 20
prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)


class Llama(BaseLLM, BaseModel):
    async def _agenerate(
            self, prompts: List[str], stop: Optional[List[str]] = None
    ) -> LLMResult:
        response = ""
        async for token in generate(prompt=prompts[0]):
            response += token
            self.callback_manager.on_llm_new_token(token, verbose=True)

        generations = [[Generation(text=response)]]
        return LLMResult(generations=generations)

    def _generate(
            self, prompts: List[str], stop: Optional[List[str]] = None
    ) -> LLMResult:
        result = None

        def run_coroutine_in_new_loop():
            nonlocal result
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                result = new_loop.run_until_complete(self._agenerate(prompts, stop))
            finally:
                new_loop.close()

        result_thread = threading.Thread(target=run_coroutine_in_new_loop)
        result_thread.start()
        result_thread.join()

        return result
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        result = self._generate([prompt], stop)
        return result.generations[0][0].text

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {}

    @property
    def _llm_type(self) -> str:
        return "llama"

# define our LLM
llm_predictor = LLMPredictor(llm=Llama())

service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

# Load the your data
documents = SimpleDirectoryReader('./data').load_data()
index = GPTListIndex.from_documents(documents, service_context=service_context)

# Query and print response
response = index.query("Hello this is the server starting message!")
logger.info(response)