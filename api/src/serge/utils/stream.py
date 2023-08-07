import re

from typing import Any

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import RedisChatMessageHistory
from langchain.schema import LLMResult
from loguru import logger
from redis import Redis


# Not used yet. WIP
class ChainRedisHandler(StreamingStdOutCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""

    def __init__(self, id: str):
        logger.debug(f"Setting up ChainRedisHandler with id {id}")
        super().__init__()
        self.id = id
        self.client = Redis(host='localhost', port=6379, decode_responses=False)
        logger.info(f"Connected to Redis? {self.client.ping()}")
        logger.info(f"Stream key : {self.stream_key}")

    @property
    def stream_key(self):
        return "stream:" + self.id

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any) -> None:
        super().on_llm_start(serialized, prompts, **kwargs)
        logger.info("starting")
        self.client.set(self.stream_key, "")
        """Run when LLM starts running."""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        super().on_llm_start(token, **kwargs)
        logger.info(token)
        self.client.append(self.stream_key, token)

        """Run on new LLM token. Only available when streaming is enabled."""

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        super().on_llm_end(response, **kwargs)
        self.client.set(self.stream_key, "")

        """Run when LLM ends running."""

    def on_llm_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        super().on_llm_error(error, **kwargs)
        self.client.set(self.stream_key, str(error))
        """Run when LLM errors."""


def get_prompt(history: RedisChatMessageHistory, params):
    """
    Get the prompt for the LLM from the chat history.
    """

    def tokenize_content(content):
        split_content = list(filter(None, re.split("([^\\n\.\?!]+[\\n\.\?! ]+)", content)))
        split_content.reverse()
        return split_content

    def sum_prompts_lengths(prompts):
        prompt_length = 0
        for s in prompts:
            prompt_length += len(s)
        return prompt_length

    dupes = {}
    prompts = []
    messages = history.messages.copy()
    messages.reverse()
    for message in messages:
        if message.content in dupes:
            continue
        dupes[message.content] = True

        instruction = ""
        match message.type:
            case "human":
                instruction = "### Instruction: "
            case "ai":
                instruction = "### Response: "
            # case "system":
            #     instruction = "### System: "
            case _:
                continue

        stop = False
        next_prompt = ""
        tokens = tokenize_content(message.content)
        prompt_length = sum_prompts_lengths(prompts)
        for token in tokens:
            if prompt_length + len(next_prompt) + len(token) < params.n_ctx:
                next_prompt = token + next_prompt
            else:
                stop = True
        if len(next_prompt) > 0:
            prompts.append(instruction + next_prompt + "\n")
        if stop:
            break

    message_prompt = ""
    prompts.reverse()
    for next_prompt in prompts:
        message_prompt += next_prompt

    final_prompt = params.init_prompt + "\n" + message_prompt[: params.n_ctx]
    logger.debug(final_prompt)
    return final_prompt
