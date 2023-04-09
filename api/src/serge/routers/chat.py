import asyncio

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from serge.utils.generate import generate
from serge.models.chat import Chat

from serge.utils.llm import LlamaCpp
from langchain.memory import RedisChatMessageHistory
from langchain.schema import messages_to_dict, SystemMessage

from redis import Redis


def remove_matching_end(a, b):
    min_length = min(len(a), len(b))

    for i in range(min_length, 0, -1):
        if a[-i:] == b[:i]:
            return b[i:]

    return b

chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@chat_router.post("/")
async def create_new_chat(
    model: str = "7B",
    temperature: float = 0.1,
    top_k: int = 50,
    top_p: float = 0.95,
    max_length: int = 256,
    context_window: int = 512,
    repeat_last_n: int = 64,
    repeat_penalty: float = 1.3,
    init_prompt: str = "Below is an instruction that describes a task. Write a response that appropriately completes the request. The response must be accurate, concise and evidence-based whenever possible. A complete answer is always ended by [end of text].",
    n_threads: int = 4,
):
    try:
        llm = LlamaCpp(
            model_path=model,
            n_ctx=context_window,
            max_tokens=max_length,
            temperature=temperature,
            top_p=top_p, 
            repeat_penalty=repeat_penalty,
            top_k=top_k,
            last_n_tokens_size=repeat_last_n,
            n_threads=n_threads,
        )
    except:
        raise ValueError("Invalid model parameters")
    

    client = Redis()

    # create the chat
    chat = Chat(llm=llm)

    # store the parameters
    client.set(f"chat:{chat.id}", chat.json())
               
    # create the message history
    history = RedisChatMessageHistory(chat.id)
    history.append(SystemMessage(content=init_prompt))

    # add the key to the set of chats
    client.sadd("chats", chat.id)

    return chat.id


@chat_router.get("/")
async def get_all_chats():
    res = []
    client = Redis()
    
    ids = client.smembers("chats")
    
    chats: list[Chat] = []

    for id in ids:
        chat_raw = client.get(f"chat:{id}")
        chat = Chat.parse_raw(chat_raw)

        chats.append(chat)


    for chat in chats:
        history = RedisChatMessageHistory(chat.id)

        try:
            first_q = history.messages[0].content
        except IndexError:
            first_q = ""
        
        res.append(
            {
                "id": chat.id,
                "created": chat.created,
                "model": chat.llm.model_path.split("/")[-1],
                "subtitle": first_q,
            }
        )

    return res


@chat_router.get("/{chat_id}")
async def get_specific_chat(chat_id: str):
    client = Redis()

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")
    
    chat_raw = client.get(f"chat:{chat_id}")
    chat = Chat.parse_raw(chat_raw)
    
    history = RedisChatMessageHistory(chat.id)

    return { **chat, 
            "history" : messages_to_dict(history) }


@chat_router.get("/{chat_id}/history")
async def get_chat_history(chat_id: str):
    client = Redis()

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")

    history = RedisChatMessageHistory(chat_id)
    return messages_to_dict(history)


@chat_router.delete("/{chat_id}" )
async def delete_chat(chat_id: str):
    client = Redis()

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")

    client.delete(f"chat:{chat_id}")
    client.srem("chats", chat_id)

    return True


@chat_router.get("/{chat_id}/question")
async def stream_ask_a_question(chat_id: str, prompt: str):
    
    client = Redis()

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")
    
    chat_raw = client.get(f"chat:{chat_id}")
    chat = Chat.parse_raw(chat_raw)
    
    history = RedisChatMessageHistory(chat.id)

    chunks = []

    # TODO do the conversation here
    
    async def event_generator():
        full_answer = ""
        error = None
        try:
            async for output in generate(
                params=chat.parameters,
            ):
                await asyncio.sleep(0.01)

                chunks.append(output)
                full_answer += output
            
                yield {
                    "event": "message", 
                    "data": full_answer}
                
        except Exception as e:
            error = e.__str__()
            yield({"event" : "error"})
        finally:
            yield({"event" : "close"})


    return EventSourceResponse(event_generator())

# @chat_router.post("/{chat_id}/question")
# async def ask_a_question(chat_id: str, prompt: str):
#     client = Redis()

#     if not client.sismember("chats", chat_id):
#         raise ValueError("Chat does not exist")
    
#     chat_raw = client.get(f"chat:{chat_id}")
#     chat = Chat.parse_raw(chat_raw)
    
#     history = RedisChatMessageHistory(chat.id)

#     llm = Llam

#     try:
#         async for output in generate(
#             prompt=full_prompt,
#             params=chat.parameters,
#         ):
#             await asyncio.sleep(0.01)
#             answer += output
#     except Exception as e:
#             error = e.__str__()
#     finally:
#         await on_close(chat, prompt, answer=answer[len(full_prompt)+1:], error=error)

#     return {"question" : prompt, "answer" : answer[len(full_prompt)+1:]}