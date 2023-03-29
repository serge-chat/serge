import subprocess, os
from serge.models.chat import Chat, ChatParameters
import asyncio
import logging

logger = logging.getLogger(__name__)


async def generate(
    prompt: str,
    chat_id: str,
    params: ChatParameters
):
    CHUNK_SIZE = 64
    await params.fetch_all_links()

    args = (
        "llama-rs",
        "--model-path",
        "/usr/src/app/weights/" + params.model + ".bin",
        "--prompt",
        prompt,
        "--num-predict",
        str(params.max_length),
        "--temp",
        str(params.temperature),
        "--top-k",
        str(params.top_k),
        "--top-p",
        str(params.top_p),
        "--repeat-last-n",
        str(params.repeat_last_n),
        "--repeat-penalty",
        str(params.repeat_penalty),
        "--num-ctx-tokens",
        str(params.context_window),
        "--num-threads",
        str(params.n_threads),
        "--persist-session",
        "/data/convs/" + chat_id,
        "--float16"
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
                raise ValueError(f"RETURN CODE {return_code}\n\n"+error_output.decode("utf-8"))
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

    prompt = ""

    if chat.questions == None:
        prompt = chat.parameters.init_prompt + "\n\n"

    prompt += "\n\n### Instruction:\n" + simple_prompt + "\n"
    prompt += "\n### Response:\n"

    return prompt
