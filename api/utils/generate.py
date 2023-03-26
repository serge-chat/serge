import subprocess, os
from models import Chat, ChatParameters
import asyncio
import logging

logger = logging.getLogger(__name__)


async def generate(
    prompt: str,
    params: ChatParameters
):
    CHUNK_SIZE = 4
    await params.fetch_all_links()

    args = (
        "llama",
        "--model",
        "/usr/src/app/weights/" + params.model,
        "--prompt",
        prompt,
        "--n_predict",
        str(params.max_length),
        "--temp",
        str(params.temperature),
        "--top_k",
        str(params.top_k),
        "--top_p",
        str(params.top_p),
        "--repeat_last_n",
        str(params.repeat_last_n),
        "--repeat_penalty",
        str(params.repeat_penalty),
        "--ctx_size",
        str(params.context_window),
        "--threads",
        str(params.n_threads),
        "--n_parts",
        "1",
    )

    logger.debug(f"Calling LLaMa with arguments", args)
    procLlama = await asyncio.create_subprocess_exec(
        *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    
    while True:
        chunk = await procLlama.stdout.read(CHUNK_SIZE)

        if not chunk:
            return_code = await procLlama.wait()

            if return_code != 0:
                error_output = await procLlama.stderr.read()
                logger.error(error_output.decode("utf-8"))
                raise ValueError(error_output.decode("utf-8"))
            else:
                return

        try:
            chunk = chunk.decode("utf-8")
        except UnicodeDecodeError:
            return

        yield chunk


async def get_full_prompt_from_chat(chat: Chat, simple_prompt: str):
    await chat.fetch_all_links()
    
    await chat.parameters.fetch_link(ChatParameters.init_prompt)

    prompt = chat.parameters.init_prompt + "\n\n"
    
    if chat.questions != None:
        for question in chat.questions:
            if question.error != None: # skip errored out prompts
                continue
            prompt += "### Instruction:\n" + question.question + "\n"
            prompt += "### Response:\n" + question.answer + "\n"

    prompt += "### Instruction:\n" + simple_prompt + "\n"
    prompt += "### Response:\n"

    return prompt
