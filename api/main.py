from fastapi import FastAPI, APIRouter
import subprocess, os

from models import LastModelUsed
from initiate_database import initiate_database
from models import Question, Chat, LastModelUsed
from generate import generate, get_full_prompt_from_chat

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


@app.on_event("startup")
async def start_database():
    await initiate_database()
    await LastModelUsed.find_all().delete()
    await LastModelUsed(name="").create()


@app.get("/models", tags=["misc."])
def list_of_installed_models():
    files = os.listdir("models")

    if "put_your_models_here.txt" in files:
        files.remove("put_your_models_here.txt")

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
async def create_new_chat():
    chat = await Chat().create()
    return chat.id


@app.get("/chat/{chat_id}", tags=["chats"])
async def get_specific_chat(chat_id: str):
    chat = await Chat.get(chat_id)
    await chat.fetch_all_links()

    return chat


@app.post("/chat/{chat_id}/question", tags=["chats"])
async def ask_a_question(chat_id: str, prompt: str):
    chat = await Chat.get(chat_id)

    full_prompt = await get_full_prompt_from_chat(chat, prompt)

    answer = await generate(prompt=full_prompt)

    question = await Question(
        question=prompt, answer=answer[len(full_prompt) :]
    ).create()

    if chat.questions is None:
        chat.questions = [question]
    else:
        chat.questions.append(question)

    await chat.save()

    return question


@app.get("/chats", tags=["chats"])
async def get_all_chats_id():
    return [i.id for i in await Chat.find_all().to_list()]
