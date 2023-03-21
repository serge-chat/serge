import os, asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from beanie.odm.enums import SortDirection

from sse_starlette.sse import EventSourceResponse
from utils.initiate_database import initiate_database
from utils.generate import generate, get_full_prompt_from_chat
from utils.convert import convert_all
from models import Question, Chat, ChatParameters

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


@app.on_event("startup")
async def start_database():
    await initiate_database()
    convert_all("weights/", "weights/tokenizer.model")


@app.get("/models", tags=["misc."])
def list_of_installed_models():
    files = os.listdir("weights")

    files = list(filter(lambda x: x.endswith(".bin"), files))

    return files


@app.post("/generate_raw", tags=["misc."])
async def generate_text_without_prompt_manipulation(
    prompt: str,
    temp: float = 0.8,
    top_k: int = 40,
    top_p: float = 0.9,
    repeast_last_n: int = 64,
    repeat_penalty: float = 1.3,
    model: str = "ggml-alpaca-13b-q4.bin",
):

    answer = await generate(
        prompt=prompt,
        temp=temp,
        top_k=top_k,
        top_p=top_p,
        repeast_last_n=repeast_last_n,
        repeat_penalty=repeat_penalty,
        model=model,
    )

    return {"question": prompt, "answer": answer[len(answer) :]}


@app.post("/chat", tags=["chats"])
async def create_new_chat(
    model: str = "ggml-alpaca-13b-q4.bin",
    temperature: float = 0.1,
    top_k: int = 50,
    top_p: float = 0.95,
    max_length: int = 256,
    repeat_last_n: int = 64,
    repeat_penalty: float = 1.3,
):
    parameters = await ChatParameters(
        model=model,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        max_length=max_length,
        repeat_last_n=repeat_last_n,
        repeat_penalty=repeat_penalty,
    ).create()

    chat = await Chat(parameters=parameters).create()
    return chat.id


@app.get("/chat/{chat_id}", tags=["chats"])
async def get_specific_chat(chat_id: str):
    chat = await Chat.get(chat_id)
    await chat.fetch_all_links()

    return chat


async def on_close(chat, prompt, answer):
    question = await Question(question=prompt.rstrip(), answer=answer.rstrip()).create()

    if chat.questions is None:
        chat.questions = [question]
    else:
        chat.questions.append(question)

    await chat.save()


@app.get("/chat/{chat_id}/question")
async def stream_ask_a_question(chat_id: str, prompt: str):
    chat = await Chat.get(chat_id)
    full_prompt = await get_full_prompt_from_chat(chat, prompt)
    answer = ""

    async def event_generator():
        nonlocal answer
        try:
            async for output in generate(
                prompt=full_prompt,
                temp=chat.parameters.temperature,
                top_k=chat.parameters.top_k,
                top_p=chat.parameters.top_p,
                repeast_last_n=chat.parameters.repeat_last_n,
                repeat_penalty=chat.parameters.repeat_penalty,
                model=chat.parameters.model,
            ):
                await asyncio.sleep(0.1)
                answer += output
                yield {"event": "message", "data": output}
        finally:
            await on_close(chat, prompt, answer)

    return EventSourceResponse(event_generator())


@app.get("/chats", tags=["chats"])
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
