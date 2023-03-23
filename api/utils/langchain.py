from langchain.llms.base import LLM
from llama_index import SimpleDirectoryReader, LangchainEmbedding, GPTListIndex, PromptHelper
from llama_index import LLMPredictor
from transformers import pipeline
from typing import Optional, List, Mapping, Any
from utils.generate import generate 
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage

# define prompt helper
# set maximum input size
max_input_size = 2048
# set number of output tokens
num_output = 256
# set maximum chunk overlap
max_chunk_overlap = 20
prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)


class CustomLLM(LLM):

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        prompt_length = len(prompt)
        response = self. generate(prompt, max_new_tokens=num_output)[0]

        # only return newly generated tokens
        return response[prompt_length:]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"name_of_model": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "custom"

# define our LLM
llm_predictor = LLMPredictor(llm=CustomLLM(callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

# Load the your data
documents = SimpleDirectoryReader('./data').load_data()
index = GPTListIndex(documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper)

# Query and print response
response = new_index.query("Hello how are you!")
print(response)