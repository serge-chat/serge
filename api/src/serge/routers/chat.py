import asyncio
import logging
import os
import psutil
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from beanie.odm.enums import SortDirection

from serge.models.chat import Question, Chat,ChatParameters
from serge.utils.generate import generate, get_full_prompt_from_chat
from serge.dependencies import dep_models_ready

async def on_close(chat, prompt, answer=None, error=None):
    question = await Question(question=prompt.rstrip(), 
                              answer=answer.rstrip() if answer != None else None, 
                              error=error).create()

    if chat.questions is None:
        chat.questions = [question]
    else:
        chat.questions.append(question)

    await chat.save()


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

# Define a logger for the current module
logger = logging.getLogger(__name__)

settings = Settings()

tags_metadata = [
    {
        "name": "misc.",
        "description": "Miscellaneous endpoints that don't fit anywhere else",
    },
    {
        "name": "chats",
        "description": "Used to manage chats",
    },
]

description = """
Serge answers your questions poorly using LLaMa/alpaca. 🚀
"""

app = FastAPI(
    title="Serge", version="0.0.1", description=description, tags_metadata=tags_metadata
)

api_app = FastAPI(title="Serge API")
app.mount('/api', api_app)

if settings.NODE_ENV == "production":
    @app.middleware("http")
    async def add_custom_header(request, call_next):
        response = await call_next(request)
        if response.status_code == 404:
            return FileResponse('static/200.html')
        return response

    @app.exception_handler(404)
    def not_found(request, exc):
        return FileResponse('static/200.html')

    async def homepage(request):
        return FileResponse('static/200.html')

    app.route('/', homepage)
    app.mount('/', StaticFiles(directory='static'))

if settings.NODE_ENV == "development":
    start_app = api_app
else:
    start_app = app

origins = [
    "http://localhost",
    "http://api:9124",
    "http://localhost:9123",
    "http://localhost:9124",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_IS_READY: bool = False


def dep_models_ready() -> list[str]:
    """
    FastAPI dependency that checks if models are ready.

    Returns a list of available models
    """
    if MODEL_IS_READY is False:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "models are not ready"
            }
        )

    files = os.listdir("/usr/src/app/weights")
    files = list(filter(lambda x: x.endswith(".bin"), files))
    return files


async def convert_model_files():
    global MODEL_IS_READY
    await anyio.to_thread.run_sync(convert_all, "/usr/src/app/weights/", "/usr/src/app/weights/tokenizer.model")
    MODEL_IS_READY = True
    logger.info("models are ready")


@start_app.on_event("startup")
async def start_database():
    logger.info("initializing database connection")
    await initiate_database()

    logger.info("initializing models")
    asyncio.create_task(convert_model_files())


@api_app.get("/models", tags=["misc."])
def list_of_installed_models(
        models: Annotated[list[str], Depends(dep_models_ready)]
):
    return models

THREADS = len(psutil.Process().cpu_affinity())

@api_app.post("/chat", tags=["chats"])
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
    n_threads: int = THREADS / 2,
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
        res.append(
            {
                "id": i.id,
                "created": i.created,
                "model": i.parameters.model,
                "subtitle": first_q,
            }
        )

    return res


@chat_router.get("/{chat_id}")
async def get_specific_chat(chat_id: str):
    chat = await Chat.get(chat_id)
    await chat.fetch_all_links()

    return chat

@chat_router.delete("/{chat_id}" )
async def delete_chat(chat_id: str):
    chat = await Chat.get(chat_id)
    deleted_chat = await chat.delete()

    if deleted_chat:
        return {"message": f"Deleted chat with id: {chat_id}"}
    else:
        raise HTTPException(status_code=404, detail="No chat found with the given id.")



@chat_router.get("/{chat_id}/question", dependencies=[Depends(dep_models_ready)])
async def stream_ask_a_question(chat_id: str, prompt: str):
    
    chat = await Chat.get(chat_id)
    await chat.fetch_link(Chat.parameters)

    full_prompt = await get_full_prompt_from_chat(chat, prompt)
    
    chunks = []

    async def event_generator():
        full_answer = ""
        error = None
        try:
            async for output in generate(
                prompt=full_prompt,
                params=chat.parameters,
            ):
                await asyncio.sleep(0.1)

                chunks.append(output)
                full_answer += output
                
                if full_prompt in full_answer:
                    cleaned_chunk = remove_matching_end(full_prompt, output)
                    yield {
                        "event": "message", 
                        "data": cleaned_chunk}
                
        except Exception as e:
            error = e.__str__()
            yield({"event" : "error"})
        finally:
            answer = "".join(chunks)[len(full_prompt)+1:]
            await on_close(chat, prompt, answer, error)
            yield({"event" : "close"})


    return EventSourceResponse(event_generator())

@chat_router.post("/{chat_id}/question", dependencies=[Depends(dep_models_ready)])
async def ask_a_question(chat_id: str, prompt: str):
    chat = await Chat.get(chat_id)
    await chat.fetch_link(Chat.parameters)

    full_prompt = await get_full_prompt_from_chat(chat, prompt)
    
    answer = ""
    error = None

    try:
        async for output in generate(
            prompt=full_prompt,
            params=chat.parameters,
        ):
            await asyncio.sleep(0.1)
            answer += output
    except Exception as e:
            error = e.__str__()
    finally:
        await on_close(chat, prompt, answer=answer[len(full_prompt)+1:], error=error)

    return {"question" : prompt, "answer" : answer[len(full_prompt)+1:]}