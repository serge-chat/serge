import asyncio

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