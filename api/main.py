from typing import Union
from fastapi import FastAPI
import subprocess, os

app = FastAPI()


@app.get("/generate")
def generate(
    model: str = "ggml-alpaca-13b-q4.bin",
    prompt: str = "What is the first letter of the alphabet?",
    temp: float = 0.8,
    top_k: int = 40,
    top_p: float = 0.9,
    repeast_last_n: int = 64,
    repeat_penalty: float = 1.3,
    stop_token: str = None,
):

    prompter = (
        lambda prompt: f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{prompt}

### Response:
"""
    )

    args = (
        "llama",
        "--model",
        "weights/" + model,
        "--prompt",
        prompter(prompt),
        "--temp",
        str(temp),
        "--top_k",
        str(top_k),
        "--top_p",
        str(top_p),
    )

    print(args)

    procLlama = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        if procLlama.poll() is not None:
            break

    output = procLlama.stdout.read().decode("utf-8")

    splits = output.split("###")

    return {
        "input": splits[1].lstrip(" Instruction:\n").rstrip("\n\n"),
        "output": splits[2].lstrip(" Response:\n"),
    }


@app.get("/models")
def models():
    files = os.listdir("weights")
    files.remove("put_your_weights_here.txt")

    return files
