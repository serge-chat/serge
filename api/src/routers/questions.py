import asyncio
from fastapi import Depends
from sse_starlette.sse import EventSourceResponse

from chat import chat_router
from models import Question, Chat
from utils.generate import generate, get_full_prompt_from_chat
from ..dependencies import dep_models_ready

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