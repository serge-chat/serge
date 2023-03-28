from fastapi import APIRouter, HTTPException
from serge.models.chat import Chat, ChatParameters
from beanie.odm.enums import SortDirection

chat_router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@chat_router.post("/")
async def create_new_chat(
    model: str = "ggml-alpaca-7B-q4_0.bin",
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


