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
import sys

sys.path.append("./build/")

import fastLlama

MODEL_PATH = "/usr/src/weights/ggml-alpaca-30B-q4_0.bin"

def stream_token(x: str) -> None:
    """
    This function is called by the llama library to stream tokens
    """
    print(x, end='', flush=True)


model = fastLlama.Model(
        path=MODEL_PATH, #path to model
        num_threads=8, #number of threads to use
        n_ctx=512, #context size of model
        last_n_size=64, #size of last n tokens (used for repetition penalty) (Optional)
        seed=0 #seed for random number generator (Optional)
    )

prompt = """Transcript of a dialog, where the User interacts with an Assistant named Bob. Bob is helpful, kind, honest, good at writing, and never fails to answer the User's requests immediately and with precision.

User: Hello, Bob.
Bob: Hello. How may I help you today?
User: Please tell me the largest city in Europe.
Bob: Sure. The largest city in Europe is Moscow, the capital of Russia.
User: """

print("\nIngesting model with prompt...")
res = model.ingest(prompt) #ingest model with prompt

if res != True:
    print("\nFailed to ingest model")
    exit(1)

print("\nModel ingested")

res = model.save_state("./models/fast_llama.bin") #save model state

res = model.load_state("./models/fast_llama.bin") #load model state
if not res:
    print("\nFailed to load the model")
    exit(1)


class CustomLLM(LLM):

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        prompt_length = len(prompt)
        response = self. generate(prompt, max_new_tokens=num_output)[0]
        print("\nGenerating from model...")
        print("")

        res = model.generate(
            num_tokens=100, 
            top_p=0.95, #top p sampling (Optional)
            temp=0.8, #temperature (Optional)
            repeat_penalty=1.0, #repetition penalty (Optional)
            streaming_fn=stream_token, #streaming function
            stop_word="User:" #stop generation when this word is encountered (Optional)
    )
        # only return newly generated tokens
        return res

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"name_of_model": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "alpaca"

# define our LLM
llm_predictor = LLMPredictor(llm=CustomLLM(callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])))

# Load the your data
documents = SimpleDirectoryReader('./data').load_data()
index = GPTListIndex(documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper)

# Query and print response
response = new_index.query("Hello how are you!")
print(response)