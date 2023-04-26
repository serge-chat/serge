from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from serge.models.chat import Chat, ChatParameters

from llama_cpp import Llama
from serge.utils.stream import get_prompt
from langchain.memory import RedisChatMessageHistory
from langchain.schema import messages_to_dict, SystemMessage
from redis import Redis
import os

from loguru import logger

logger.debug("Starting redis client")
R = Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=int(os.environ.get("REDIS_PORT", "6379")))

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
    init_prompt: str = "Below is an instruction that describes a task. Write a response that appropriately completes the request.",
    n_threads: int = 4,
):
    try:
        client = Llama(
                        model_path="/usr/src/app/weights/"+model+".bin",
                        )
        del client
    except:
        raise ValueError("Model can't be found")
    

    client = R

    params = ChatParameters(
        model_path=model,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        max_tokens=max_length,
        n_ctx=context_window,
        last_n_tokens_size=repeat_last_n,
        repeat_penalty=repeat_penalty,
        n_threads=n_threads,
    )
    # create the chat
    chat = Chat(params=params)

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
    client = R
    
    ids = client.smembers("chats")
    
    chats = sorted([await get_specific_chat(id.decode()) for id in ids],
                   key=lambda x: x["created"], 
                   reverse=True)

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
                "subtitle": subtitle
            }
        )

    return res


@chat_router.get("/{chat_id}")
async def get_specific_chat(chat_id: str):
    client = R

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")
    
    chat_raw = client.get(f"chat:{chat_id}")
    chat = Chat.parse_raw(chat_raw)
    
    history = RedisChatMessageHistory(chat.id)

    chat_dict = chat.dict()
    chat_dict["history"] = messages_to_dict(history.messages)
    return chat_dict


@chat_router.get("/{chat_id}/history")
async def get_chat_history(chat_id: str):
    client = R

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")

    history = RedisChatMessageHistory(chat_id)
    return messages_to_dict(history.messages)


@chat_router.delete("/{chat_id}" )
async def delete_chat(chat_id: str):
    client = R

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")

    RedisChatMessageHistory(chat_id).clear()
    
    client.delete(f"chat:{chat_id}")    
    client.srem("chats", chat_id)

    return True


@chat_router.get("/{chat_id}/question")
def stream_ask_a_question(chat_id: str, prompt: str):
    client = R

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")
    
    logger.debug("creating chat")
    chat_raw = client.get(f"chat:{chat_id}")
    chat = Chat.parse_raw(chat_raw)

    logger.debug(chat.params)    
    logger.debug("creating history")
    history = RedisChatMessageHistory(chat.id)

    logger.debug(f"adding question {prompt}")

    history.add_user_message(prompt)
    prompt = get_prompt(history)
    prompt += "### Response:\n"

    logger.debug("creating Llama client")
    try:
        client = Llama(
                        model_path="/usr/src/app/weights/"+chat.params.model_path+".bin",
                        n_ctx=chat.params.n_ctx,
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
            for output in client(prompt, 
                    stream=True,
                    temperature=chat.params.temperature,
                    top_p=chat.params.top_p,
                    top_k=chat.params.top_k,
                    repeat_penalty=chat.params.repeat_penalty,
                    max_tokens=chat.params.max_tokens,
                    ):
                txt = output["choices"][0]["text"]
                full_answer += txt
                yield {
                    "event": "message", 
                    "data": txt}
                
        except Exception as e:
            if type(e) == UnicodeDecodeError:
                pass
            else: 
                error = e.__str__()
                logger.error(error)
                yield({"event" : "error"})
        finally:
            if error:
                history.append(SystemMessage(content=error))
            else:
                logger.info(full_answer)
                history.add_ai_message(full_answer)
            yield({"event" : "close"})

    return EventSourceResponse(event_generator())

@chat_router.post("/{chat_id}/question")    
async def ask_a_question(chat_id: str, prompt: str):
    client = R

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")
    
    chat_raw = client.get(f"chat:{chat_id}")
    chat = Chat.parse_raw(chat_raw)
    
    history = RedisChatMessageHistory(chat.id)
    history.add_user_message(prompt)

    prompt = get_prompt(history)
    prompt += "### Response:\n"
    
    
    try:
        client = Llama(
                    model_path="/usr/src/app/weights/"+chat.params.model_path+".bin",
                    n_ctx=chat.params.n_ctx,
                    n_threads=chat.params.n_threads,
                    last_n_tokens_size=chat.params.last_n_tokens_size,
                    )
        answer = client(prompt, 
                        temperature=chat.params.temperature,
                        top_p=chat.params.top_p,
                        top_k=chat.params.top_k,
                        repeat_penalty=chat.params.repeat_penalty,
                        max_tokens=chat.params.max_tokens,
                        )
    except Exception as e:
        error = e.__str__()
        logger.error(error)
        history.append(SystemMessage(content=error))
        return error

    history.add_ai_message(answer)
    return answer

@chat_router.post("/{chat_id}/completion")    
async def complete_a_question(chat_id: str, prompt: str):
    client = R

    if not client.sismember("chats", chat_id):
        raise ValueError("Chat does not exist")
    
    chat_raw = client.get(f"chat:{chat_id}")
    chat = Chat.parse_raw(chat_raw)
    
    history = RedisChatMessageHistory(chat.id)
    history.add_user_message(prompt)

    # djdj: try to see if past session is useful or not
    prompt = get_prompt(history)
    prompt += "### Response:\n"
    
    try:
        client = Llama(
                    model_path="/usr/src/app/weights/"+chat.params.model_path+".bin",
                    n_ctx=chat.params.n_ctx,
                    n_threads=chat.params.n_threads,
                    last_n_tokens_size=chat.params.last_n_tokens_size,
                    )
        answer = client.create_completion(prompt)
    except Exception as e:
        error = e.__str__()
        logger.error(error)
        history.append(SystemMessage(content=error))
        return error

    history.add_ai_message(prompt + '' + answer["choices"][0]["text"])  # djdj: need to update the validation to support completion as output, optional for now
    # return answer['choices'][0]["text"]  # djdj: let client to decode it
    return answer 

@chat_router.post("/semantic_search/create_embedding")    
async def create_embedding(input: str):
    client = R
    
    default_chat_id_semantic_search = "e79e415f-7650-44b0-9e65-967f6127e305"  # djdj: pre-generated chat id for creating embedding. 
    chat_raw = client.get(f"chat:{default_chat_id_semantic_search}")
    chat = Chat.parse_raw(chat_raw)

    history = RedisChatMessageHistory(chat.id)
    history.add_user_message(input)

    prompt = get_prompt(history)
    prompt += "### Response:\n"
    
    try:
        client = Llama(
                    model_path="/usr/src/app/weights/"+chat.params.model_path+".bin",
                    n_ctx=chat.params.n_ctx,
                    n_threads=chat.params.n_threads,
                    last_n_tokens_size=chat.params.last_n_tokens_size,
                    embedding=True
                    )
        answer = client.create_embedding(input=input)
    except Exception as e:
        error = e.__str__()
        logger.error(error)
        history.append(SystemMessage(content=error))
        return error

    history.add_ai_message(input + ': ' + ','.join(str(num) for num in answer["data"][0]["embedding"]))  # djdj: need to update the validation to support embedding as output, optional for now
    return answer