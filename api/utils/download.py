import argparse
import huggingface_hub
import os

from typing import List
from convert import convert_all

models_info = {
    "7B": ["Pi3141/alpaca-7B-ggml", "ggml-model-q4_0.bin"],
    "13B": ["Pi3141/alpaca-13B-ggml", "ggml-model-q4_0.bin"],
    "30B": ["Pi3141/alpaca-30B-ggml", "ggml-model-q4_0.bin"],
    "tokenizer": ["decapoda-research/llama-7b-hf", "tokenizer.model"],
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download and convert LLaMA models to the current format"
    )
    parser.add_argument(
        "model",
        help="Model name",
        nargs="+",
        choices=["7B", "13B", "30B", "tokenizer"],
    )

    return parser.parse_args()


def download_models(models: List[str]):
    for model in models:
        repo_id, filename = models_info[model]
        print(f"Downloading {model} model from {repo_id}...")

        huggingface_hub.hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir="/usr/src/app/weights",
            local_dir_use_symlinks=False,
            cache_dir="/usr/src/app/weights/.cache",
        )

        if filename == "ggml-model-q4_0.bin":
            os.rename(
                "/usr/src/app/weights/ggml-model-q4_0.bin", f"/usr/src/app/weights/ggml-alpaca-{model}-q4_0.bin"
            )


if __name__ == "__main__":
    args = parse_args()

    print("Downloading models from HuggingFace")
    download_models(args.model)

    print("Converting models to the current format")
    convert_all("/usr/src/app/weights", "/usr/src/app/weights/tokenizer.model")
