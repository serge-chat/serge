from serge.utils.llm import LlamaCpp
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import threading
import queue

class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration: raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)

class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send(token)


def llm_thread(g, prompt):
    try:
        chat = LlamaCpp(
            verbose=True,
            streaming=True,
            callback_manager=CallbackManager([ChainStreamHandler(g)]),
            temperature=0.7,
        )
        chat([SystemMessage(content="You are a poetic assistant"), HumanMessage(content=prompt)])

    finally:
        g.close()


def chat(prompt):
    g = ThreadedGenerator()
    threading.Thread(target=llm_thread, args=(g, prompt)).start()
    return g

