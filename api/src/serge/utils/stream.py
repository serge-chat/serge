from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import RedisChatMessageHistory
from redis import Redis
from loguru import logger

from typing import Any, Dict, List, Union

from langchain.schema import LLMResult


# Not used yet. WIP
class ChainRedisHandler(StreamingStdOutCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""
    def __init__(self, id:str):
        logger.debug(f"Setting up ChainRedisHandler with id {id}")
        super().__init__()
        self.id = id
        self.client = Redis()
        logger.info(f"Stream key : {self.stream_key}")
    
    @property
    def stream_key(self):
        return "stream:"+self.id

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
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

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        super().on_llm_error(error, **kwargs)
        self.client.set(self.stream_key, str(error))
        """Run when LLM errors."""


def get_prompt(history: RedisChatMessageHistory):
    """
    Get the prompt for the LLM from the chat history.
    """
    prompt = ""

    for message in history.messages:
        match message.type:
            case "human":
                prompt += "### Instruction:\n" + message.content + "\n"
            case "ai":
                prompt += "### Response:\n" + message.content + "\n"
            case "system":
                prompt += "### System:\n" + message.content + "\n"
            case _:
                pass
    
    return prompt
