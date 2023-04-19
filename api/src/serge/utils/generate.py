import subprocess, os
from serge.models.chat import Chat, ChatParameters
import asyncio
import logging
import math

logger = logging.getLogger(__name__)


async def generate(
    prompt: str,
    params: ChatParameters
):
    CHUNK_SIZE = 64
    await params.fetch_all_links()

    args = (
        "llama",
        "--model",
        "/usr/src/app/weights/" + params.model + ".bin",
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

    logger.debug(f"Calling LLaMA with arguments", args)
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

    prompt = chat.parameters.init_prompt + "\n\n"
    prompt_list = [prompt]

    # Go in reverse order and add in prompts until we reach the max context window size
    if chat.questions != None:
        for question in chat.questions[::-1]: 
            if question.error != None: # skip errored out prompts
                continue
            tmp_prompt_list = prompt_list.copy()
            tmp_prompt_list.insert(1, "### Instruction:\n" + question.question + "\n")
            tmp_prompt_list.insert(2, "### Response:\n" + question.answer + "\n")

            # The full prompt includes these at the end of the list
            tmp_full_prompt_list = tmp_prompt_list.copy()
            tmp_full_prompt_list += ["### Instruction:\n" + simple_prompt + "\n"]
            tmp_full_prompt_list += ["### Response:\n"]

            tmp_full_prompt = str.join('', tmp_full_prompt_list)
            num_tokens = math.ceil(len(tmp_full_prompt) / 4) 
            if num_tokens < (chat.parameters.context_window - 4):
                prompt_list = tmp_prompt_list.copy()
            else:
                break

    prompt = str.join('', prompt_list)
    prompt += "### Instruction:\n" + simple_prompt + "\n"
    prompt += "### Response:\n"

    return prompt
