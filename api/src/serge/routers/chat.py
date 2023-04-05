import asyncio
import redis

from fastapi import APIRouter, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from beanie.odm.enums import SortDirection

from serge.models.chat import Question, Chat,ChatParameters
from loguru import logger

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
    parameters = await ChatParameters(
        model=model,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        max_length=max_length,
        context_window=context_window,
        repeat_last_n=repeat_last_n,
        repeat_penalty=repeat_penalty,
        init_prompt=init_prompt,
        n_threads=n_threads,
    ).create()

    chat = await Chat(parameters=parameters).create()
    client = redis.Redis()

    client.rpush("load_queue", str(chat.id))
    
    while not client.sismember("loaded_chats", str(chat.id)):
        await asyncio.sleep(0.05)
    
    return chat.id


@chat_router.get("/")
async def get_all_chats():
    res = []

    for i in (
        await Chat.find_all().sort((Chat.created, SortDirection.DESCENDING)).to_list()
    ):
        await i.fetch_link(Chat.parameters)
        await i.fetch_link(Chat.questions)

        first_q = i.questions[0].question if i.questions else ""

        client = redis.Redis()
        if client.sismember("loaded_chats", str(i.id)):
            stream = client.get("stream:" + str(i.id))
            if stream != None and stream != "EOF":
                status = "streaming"
            else:
                status = "loaded"
        else:
            status = "unloaded"
        

        res.append(
            {
                "id": i.id,
                "created": i.created,
                "model": i.parameters.model,
                "subtitle": first_q,
                "status" : status
            }
        )

    return res


@chat_router.get("/{chat_id}")
async def get_specific_chat(chat_id: str):
    chat = await Chat.get(chat_id)
    await chat.fetch_all_links()

    return chat

@chat_router.get("/{chat_id}/status")
async def get_chat_status(chat_id: str):
    client = redis.Redis()
    if client.sismember("loaded_chats", chat_id):
        stream = client.get("stream:" + chat_id)
        if stream != None and stream.decode() != "EOF":
            status = "streaming"
        else:
            status = "loaded"
    else:
        status = "unloaded"
        
    return status


@chat_router.delete("/{chat_id}" )
async def delete_chat(chat_id: str):
    chat = await Chat.get(chat_id)
    deleted_chat = await chat.delete()

    client = redis.Redis()
    client.rpush("unload_queue", str(chat.id))

    
    while client.sismember("loaded_chats", str(chat.id)):
        await asyncio.sleep(0.05)
    
    if deleted_chat:
        return {"message": f"Deleted chat with id: {chat_id}"}
    else:
        raise HTTPException(status_code=404, detail="No chat found with the given id.")



@chat_router.post("/{chat_id}/question")
async def ask_a_question(chat_id: str, prompt: str):
    client = redis.Redis()
    
    logger.info(f"Asking question {prompt} to chat {chat_id}")
    client.set(f"stream:{chat_id}", "")
    
    if client.sismember("loaded_chats", chat_id):
        client.rpush(f"questions:{chat_id}", prompt)
    else:
        logger.info(f"Chat {chat_id} not loaded, loading it.")
        client.rpush("load_queue", str(chat_id))
        while not client.sismember("loaded_chats", str(chat_id)):
            await asyncio.sleep(0.05)   
        
        logger.info(f"Re-Asking question {prompt} to chat {chat_id}")
        client.rpush(f"questions:{chat_id}", prompt)
    
    return {"message": "Question added to queue."}

@chat_router.get("/{chat_id}/stream")
async def stream_chat(chat_id: str):
    client = redis.Redis()

    if client.sismember("loaded_chats", chat_id):
        stream = client.get(f"stream:{chat_id}")
        if stream != None:
            return {
                "question" : client.lindex(f"questions:{chat_id}", 1),
                "answer" : stream.decode("utf-8")}
        else:
            return {
                "question" : "",
                "answer" : ""}
    else:
        return {"message": f"Chat {chat_id} not loaded."}