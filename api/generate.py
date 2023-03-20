import subprocess, os
from models import LastModelUsed, Chat
import asyncio


async def generate(
    model: str = "ggml-alpaca-13b-q4.bin",
    prompt: str = "The sky is blue because",
    n_predict: int = 128,
    temp: float = 0.05,
    top_k: int = 50,
    top_p: float = 0.95,
    repeast_last_n: int = 64,
    repeat_penalty: float = 1.3,
):

    last_model = await LastModelUsed.find_all().to_list()
    last_model = last_model[0]

    if model != last_model.name and os.path.isfile("magic.dat"):
        print("Deleting magic.dat because model changed")

        os.remove("magic.dat")

        last_model.name = model
        await last_model.save()

    args = (
        "alpaca",
        "--model",
        "models/" + model,
        "--prompt",
        prompt,
        "--n_predict",
        str(n_predict),
        "--temp",
        str(temp),
        "--top_k",
        str(top_k),
        "--top_p",
        str(top_p),
        "--repeat_last_n",
        str(repeast_last_n),
        "--repeat_penalty",
        str(repeat_penalty),
        "--threads",
        "2",
    )

    procLlama = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        await asyncio.sleep(0.1)
        if procLlama.poll() is not None:
            break

    output = procLlama.stdout.read().decode("utf-8")
    return output


async def get_full_prompt_from_chat(chat: Chat, simple_prompt: str):
    await chat.fetch_all_links()

    prompt = """Below is an instruction that describes a task. Write a response that appropriately completes the request. The response must be accurate, concise and evidence-based whenever possible. A complete answer is always ended by [end of text].

"""
    if chat.questions != None:
        for question in chat.questions:
            prompt += "### Instruction:\n" + question.question + "\n"
            prompt += "### Response:\n" + question.answer + "\n"

    prompt += "### Instruction:\n" + simple_prompt + "\n"
    prompt += "### Response:\n"

    return prompt
