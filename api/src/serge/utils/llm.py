"""Wrapper around llama.cpp."""
from typing import Any, Dict, List, Optional

from pydantic import Field, root_validator, Extra

from langchain.llms.base import LLM

class LlamaCpp(LLM):
    """Wrapper around the llama.cpp model.

    To use, you should have the llama-cpp-python library installed, and provide the
    path to the Llama model as a named parameter to the constructor.
    Check out: https://github.com/abetlen/llama-cpp-python

    Example:
        .. code-block:: python

            from langchain.llms import LlamaCppEmbeddings
            llm = LlamaCppEmbeddings(model_path="/path/to/llama/model")
    """

    client: Any  #: :meta private:
    model_path: str
    """The path to the Llama model file."""

    n_ctx: int = Field(512, alias="n_ctx")
    """Token context window."""

    n_parts: int = Field(-1, alias="n_parts")
    """Number of parts to split the model into. 
    If -1, the number of parts is automatically determined."""

    seed: int = Field(-1, alias="seed")
    """Seed. If -1, a random seed is used."""

    f16_kv: bool = Field(False, alias="f16_kv")
    """Use half-precision for key/value cache."""

    logits_all: bool = Field(False, alias="logits_all")
    """Return logits for all tokens, not just the last token."""

    vocab_only: bool = Field(False, alias="vocab_only")
    """Only load the vocabulary, no weights."""

    use_mlock: bool = Field(False, alias="use_mlock")
    """Force system to keep model in RAM."""

    n_threads: Optional[int] = Field(None, alias="n_threads")
    """Number of threads to use. 
    If None, the number of threads is automatically determined."""

    n_batch: Optional[int] = Field(8, alias="n_batch")
    """Number of tokens to process in parallel.
    Should be a number between 1 and n_ctx."""

    max_tokens: Optional[int] = 256
    """The maximum number of tokens to generate."""

    temperature: Optional[float] = 0.8
    """The temperature to use for sampling."""

    top_p: Optional[float] = 0.95
    """The top-p value to use for sampling."""

    logprobs: Optional[int] = Field(None)
    """The number of logprobs to return. If None, no logprobs are returned."""

    echo: Optional[bool] = False
    """Whether to echo the prompt."""

    stop_sequences: Optional[List[str]] = []
    """A list of strings to stop generation when encountered."""

    repeat_penalty: Optional[float] = 1.1
    """The penalty to apply to repeated tokens."""

    top_k: Optional[int] = 40
    """The top-k value to use for sampling."""

    last_n_tokens_size: Optional[int] = 64
    """The number of tokens to look back when applying the repeat_penalty."""

    streaming: bool = False    

    class Config:
        extra = Extra.ignore

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that llama-cpp-python library is installed."""
        model_path = values["model_path"]

        try:
            from llama_cpp import Llama

        except ImportError:
            raise ModuleNotFoundError(
                "Could not import llama-cpp-python library. "
                "Please install the llama-cpp-python library to "
                "use this embedding model: pip install llama-cpp-python"
            )
        except Exception:
            raise NameError(f"Could not load Llama model from path: {model_path}")

        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling llama_cpp."""
        return {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "logprobs": self.logprobs,
            "echo": self.echo,
            "stop_sequences": self.stop_sequences,
            "repeat_penalty": self.repeat_penalty,
            "top_k": self.top_k,
            "n_threads" : self.n_threads,
            "n_ctx" : self.n_ctx,
            "n_parts" : self.n_parts,
            "seed" : self.seed,
            "f16_kv" : self.f16_kv,
            "logits_all" : self.logits_all,
            "vocab_only" : self.vocab_only,
            "use_mlock" : self.use_mlock,
            "n_batch" : self.n_batch,
            "last_n_tokens_size" : self.last_n_tokens_size,
            "streaming" : self.streaming,
        }

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {**{"model_path": self.model_path}, **self._default_params}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "llama.cpp"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Llama model and return the output.

        Args:
            prompt: The prompt to use for generation.
            stop: A list of strings to stop generation when encountered.

        Returns:
            The generated text.

        Example:
            .. code-block:: python

                from langchain.llms import LlamaCppEmbeddings
                llm = LlamaCppEmbeddings(model_path="/path/to/local/llama/model.bin")
                llm("This is a prompt.")
        """
        from llama_cpp import Llama

        params = self._identifying_params
        client = Llama(
                        model_path="/usr/src/app/weights/"+self.model_path+".bin",
                        n_ctx=self.n_ctx,
                        n_parts=self.n_parts,
                        seed=self.seed,
                        f16_kv=self.f16_kv,
                        logits_all=self.logits_all,
                        vocab_only=self.vocab_only,
                        use_mlock=self.use_mlock,
                        n_threads=self.n_threads,
                        n_batch=self.n_batch,
                        last_n_tokens_size=self.last_n_tokens_size,
                    )
        
        if self.stop_sequences and stop is not None:
            raise ValueError("`stop_sequences` found in both the input and default params.")
        elif self.stop_sequences:
            params["stop_sequences"] = self.stop_sequences
        else:
            params["stop_sequences"] = []

        if self.streaming:
            response = ""
            stream = client(
                prompt=prompt,
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
                top_p=params["top_p"],
                logprobs=params["logprobs"],
                echo=params["echo"],
                stop=params["stop_sequences"],
                repeat_penalty=params["repeat_penalty"],
                top_k=params["top_k"],
                stream=True
            )
            for stream_resp in stream:
                try:
                    token = stream_resp["choices"][0]["text"]
                except:
                    token = ""
                
                response += token

                self.callback_manager.on_llm_new_token(token, verbose=self.verbose)
            return response

        else:
            """Call the Llama model and return the output."""
            output = client(
                prompt=prompt,
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
                top_p=params["top_p"],
                logprobs=params["logprobs"],
                echo=params["echo"],
                stop=params["stop_sequences"],
                repeat_penalty=params["repeat_penalty"],
                top_k=params["top_k"],
            )
            text = output["choices"][0]["text"]

            return text

if __name__ == "__main__":
    from langchain.callbacks.base import CallbackManager
    from serge.utils.stream import ChainRedisHandler

    llm = LlamaCpp(streaming=True, model_path="gpt4all", 
                   callback_manager=CallbackManager([ChainRedisHandler("1")]),
                    verbose=True, temperature=0.1, max_tokens=128)

    input()
    resp = llm("Write a paragraph about France please.")
