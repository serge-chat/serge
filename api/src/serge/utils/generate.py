import subprocess
import os
from serge.models.chat import Chat, ChatParameters
import asyncio
import logging

logger = logging.getLogger(__name__)


async def generate(
    prompt: str,
    params: ChatParameters
):
    CHUNK_SIZE = 128
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
        str(params.context_window if params.context_window > 2048 else 2048),
        "--threads",
        str(params.n_threads),
        "--n_parts",
        "1",
    )

    logger.debug(f"Calling LLaMa with arguments", args)
    procLlama = await asyncio.create_subprocess_exec(
        *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    # start off with the length our our prompt in chunks below zero. everything above zero is the ai's response
    outputLength = len(prompt)*-1 - 64
    lastchunk = ""
    while True:
        chunk = await procLlama.stdout.read(CHUNK_SIZE)

        if not chunk:
            yield lastchunk
            return_code = await procLlama.wait()

            if return_code != 0:
                error_output = await procLlama.stderr.read()
                logger.error(error_output.decode("utf-8"))
                raise ValueError(
                    f"RETURN CODE {return_code}\n\n"+error_output.decode("utf-8"))
            else:
                return

        try:
            chunk = chunk.decode("utf-8")
            if (outputLength > 0):  # if the ai has started responding, log the chunk and length
                logger.warn("a chunk: "+chunk)
                # combine the last two chunks to make sure that if the ### was on a border between chunks we still detect it
                index = (lastchunk+chunk).find("###")
                if (index != -1):  # detect the ai responding to itself
                    # logger.warn("bad response: "+lastchunk+"|"+chunk);
                    # find which cunk it was in
                    if (index < len(lastchunk)):  # it was the last chunk
                        logger.warn(
                            "AI responded to itself in the last chunk, cropping response")
                        # remove everything after the ai's response
                        lastchunk = lastchunk[:index]
                        yield lastchunk  # return only cropped chunk
                    else:
                        logger.warn(
                            "AI responded to itself in the current chunk, cropping response")
                        # adjust the index to be in the current chunk
                        index -= len(lastchunk)
                        # remove everything after the ai's response
                        chunk = chunk[:index]
                        yield lastchunk  # return the ok chunk
                        yield chunk  # return the cropped chunk
                    # either way kill llama and finish the response
                    procLlama.kill()  # stop llama from continuing to respond
                    return_code = 0  # not sure if this is needed
                    return  # stop the generator
            else:
                logger.warn("u chunk: "+chunk)
                outputLength += len(chunk)  # incremet the length of the prompt
        except UnicodeDecodeError:
            return

        yield lastchunk
        lastchunk = chunk


async def get_full_prompt_from_chat(chat: Chat, simple_prompt: str):
    await chat.fetch_all_links()

    await chat.parameters.fetch_link(ChatParameters.init_prompt)

    prompt = chat.parameters.init_prompt + "\n\n"

    if chat.questions != None:
        for question in chat.questions:
            if question.error != None:  # skip errored out prompts
                continue
            prompt += "### Instruction:\n" + question.question + "\n"
            prompt += "### Response:\n" + question.answer + "\n"

    prompt += "### Instruction:\n" + simple_prompt + "\n"
    prompt += "### Response:\n"

    return prompt
