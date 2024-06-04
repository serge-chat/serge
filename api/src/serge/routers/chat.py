import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from langchain.memory import RedisChatMessageHistory
from langchain.schema import AIMessage, HumanMessage, SystemMessage, messages_to_dict
from llama_cpp import Llama
from loguru import logger
from redis import Redis
from sse_starlette.sse import EventSourceResponse

from serge.models.chat import Chat, ChatParameters
from serge.models.user import User, UserAuth
from serge.routers.auth import get_current_active_user, get_current_user
from serge.utils.stream import get_prompt

chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


def _try_get_chat(client, chat_id, u):
    if not isinstance(u, (User, UserAuth)):
        raise ValueError("Call must be authenticated.")

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")

    chat_raw = client.get(f"chat:{chat_id}")
    chat = Chat.parse_raw(chat_raw)

    # backwards compat
    if not hasattr(chat, "owner"):
        chat.owner = "system"

    if chat.owner != u.username:
        raise ValueError(f"Chat not owned by user: {u.username}")
    return chat


@chat_router.post("/")
async def create_new_chat(
    u: User = Depends(get_current_active_user),
    model: str = "7B",
    temperature: float = 0.1,
    top_k: int = 50,
    top_p: float = 0.95,
    max_length: int = 2048,
    context_window: int = 2048,
    gpu_layers: Optional[int] = None,
    repeat_last_n: int = 64,
    repeat_penalty: float = 1.3,
    init_prompt: str = "Below is an instruction that describes a task. Write a response that appropriately completes the request.",
    n_threads: int = 4,
):
    if not os.path.exists(f"/usr/src/app/weights/{model}.bin"):
        raise ValueError(f"Model can't be found: /usr/src/app/weights/{model}.bin")

    client = Redis(host="localhost", port=6379, decode_responses=False)

    params = ChatParameters(
        model_path=model,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        max_tokens=max_length,
        n_ctx=context_window,
        n_gpu_layers=gpu_layers,
        last_n_tokens_size=repeat_last_n,
        repeat_penalty=repeat_penalty,
        n_threads=n_threads,
        init_prompt=init_prompt,
    )
    # create the chat
    chat = Chat(owner=u.username, params=params)

    # store the parameters
    client.set(f"chat:{chat.id}", chat.json())

    # create the message history
    history = RedisChatMessageHistory(chat.id)
    history.append(SystemMessage(content=init_prompt))

    # add the key to the set of chats
    client.sadd("chats", chat.id)

    return chat.id


@chat_router.get("/")
async def get_all_chats(u: User = Depends(get_current_active_user)):
    res = []
    client = Redis(host="localhost", port=6379, decode_responses=False)
    ids = client.smembers("chats")
    chats = []
    for id in ids:
        try:
            chats.append(await get_specific_chat(id.decode(), u))
        except:
            pass  # skip access denied

    chats = sorted(
        chats,
        key=lambda x: x["created"],
        reverse=True,
    )

    for chat in chats:
        try:
            subtitle = chat["history"][-1]["data"]["content"]
        except (KeyError, IndexError):
            subtitle = ""
        res.append(
            {
                "id": chat["id"],
                "created": chat["created"],
                "model": chat["params"]["model_path"],
                "subtitle": subtitle,
            }
        )

    return res


@chat_router.get("/{chat_id}")
async def get_specific_chat(chat_id: str, u: User = Depends(get_current_active_user)):
    client = Redis(host="localhost", port=6379, decode_responses=False)
    chat = _try_get_chat(client, chat_id, u)

    history = RedisChatMessageHistory(chat.id)
    chat_dict = chat.dict()
    chat_dict["history"] = messages_to_dict(history.messages)
    return chat_dict


@chat_router.get("/{chat_id}/history")
async def get_chat_history(chat_id: str, u: User = Depends(get_current_active_user)):
    client = Redis(host="localhost", port=6379, decode_responses=False)
    _ = _try_get_chat(client, chat_id, u)

    history = RedisChatMessageHistory(chat_id)
    return messages_to_dict(history.messages)


@chat_router.delete("/{chat_id}/prompt")
async def delete_prompt(
    chat_id: str, idx: int, u: User = Depends(get_current_active_user)
):
    client = Redis(host="localhost", port=6379, decode_responses=False)
    _ = _try_get_chat(client, chat_id, u)

    history = RedisChatMessageHistory(chat_id)

    if idx >= len(history.messages):
        logger.error("Unable to delete message, chat in progress")
        raise HTTPException(
            status_code=202, detail="Unable to delete message, chat in progress"
        )

    messages = history.messages.copy()[:idx]
    history.clear()

    for message in messages:
        history.append(message)

    return True


@chat_router.delete("/{chat_id}")
async def delete_chat(chat_id: str, u: User = Depends(get_current_active_user)):
    client = Redis(host="localhost", port=6379, decode_responses=False)
    _ = _try_get_chat(client, chat_id, u)

    RedisChatMessageHistory(chat_id).clear()

    client.delete(f"chat:{chat_id}")
    client.srem("chats", chat_id)

    return True


@chat_router.delete("/delete/all")
async def delete_all_chats():
    client = Redis(host="localhost", port=6379, decode_responses=False)
    client.flushdb()
    return True


@chat_router.get("/{chat_id}/question")
async def stream_ask_a_question(
    chat_id: str, prompt: str, u: User = Depends(get_current_active_user)
):
    logger.info("Starting redis client")

    client = Redis(host="localhost", port=6379, decode_responses=False)

    chat = _try_get_chat(client, chat_id, u)

    logger.debug(chat.params)
    logger.debug("creating history")
    history = RedisChatMessageHistory(chat.id)

    if len(prompt) > 0:
        logger.debug(f"adding question {prompt}")
        human_message = HumanMessage(content=prompt)
        history.append(message=human_message)
    prompt = get_prompt(history, chat.params)
    prompt += "### Response:\n"

    logger.debug("creating Llama client")
    try:
        client = Llama(
            model_path=f"/usr/src/app/weights/{chat.params.model_path}.bin",
            n_ctx=len(chat.params.init_prompt) + chat.params.n_ctx,
            n_gpu_layers=chat.params.n_gpu_layers,
            n_threads=chat.params.n_threads,
            last_n_tokens_size=chat.params.last_n_tokens_size,
        )
    except ValueError as e:
        error = e.__str__()
        logger.error(error)
        history.append(SystemMessage(content=error))
        return {"event": "error"}

    def event_generator():
        full_answer = ""
        error = None
        try:
            for output in client(
                prompt,
                stream=True,
                temperature=chat.params.temperature,
                top_p=chat.params.top_p,
                top_k=chat.params.top_k,
                repeat_penalty=chat.params.repeat_penalty,
                max_tokens=chat.params.max_tokens,
            ):
                txt = output["choices"][0]["text"]
                full_answer += txt
                yield {"event": "message", "data": txt}

        except Exception as e:
            if type(e) == UnicodeDecodeError:
                pass
            else:
                error = e.__str__()
                logger.error(error)
                yield ({"event": "error"})
        finally:
            if error:
                history.append(SystemMessage(content=error))
            else:
                logger.info(full_answer)
                ai_message = AIMessage(content=full_answer)
                history.append(message=ai_message)
            yield ({"event": "close"})

    return EventSourceResponse(event_generator())


@chat_router.post("/{chat_id}/question")
async def ask_a_question(
    chat_id: str, prompt: str, u: User = Depends(get_current_active_user)
):
    client = Redis(host="localhost", port=6379, decode_responses=False)
    chat = _try_get_chat(client, chat_id, u)
    history = RedisChatMessageHistory(chat.id)

    if len(prompt) > 0:
        human_message = HumanMessage(content=prompt)
        history.append(message=human_message)

    prompt = get_prompt(history, chat.params)
    prompt += "### Response:\n"

    try:
        client = Llama(
            model_path=f"/usr/src/app/weights/{chat.params.model_path}.bin",
            n_ctx=len(chat.params.init_prompt) + chat.params.n_ctx,
            n_threads=chat.params.n_threads,
            n_gpu_layers=chat.params.n_gpu_layers,
            last_n_tokens_size=chat.params.last_n_tokens_size,
        )
        answer = client(
            prompt,
            temperature=chat.params.temperature,
            top_p=chat.params.top_p,
            top_k=chat.params.top_k,
            repeat_penalty=chat.params.repeat_penalty,
            max_tokens=chat.params.max_tokens,
        )
        full_answer = ""
        if len(answer.get("choices", [])) > 0:
            full_answer = answer["choices"][0].get("text", "")
    except Exception as e:
        error = e.__str__()
        logger.error(error)
        history.append(SystemMessage(content=error))
        return error

    if not isinstance(answer, str):
        answer = str(answer)

    ai_message = AIMessage(content=full_answer)
    history.append(message=ai_message)
    return answer
