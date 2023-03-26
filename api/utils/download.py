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
        if os.path.isfile(f"weights/ggml-alpaca-{model}-q4_0.bin"):
            print(f"The model ggml-alpaca-{model}-q4_0.bin already exists in the weights/ folder, skipping download.")
            continue
        print("Downloading models from HuggingFace")
        repo_id, filename = models_info[model]
        print(f"Downloading {model} model from {repo_id}...")

        try :
            huggingface_hub.hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir="/usr/src/app/weights",
                local_dir_use_symlinks=False,
                cache_dir="/usr/src/app/weights/.cache",
            )
        except :
            if(model != "tokenizer"):
                print(f"Download failed, try it again later. You can also download the model manually from https://huggingface.co/Pi3141/alpaca-{model}-ggml/resolve/main/ggml-model-q4_0.bin and put it in the weights/ folder.")
                print(f"Then rename it to ggml-alpaca-{model}-q4_0.bin and run the script again.")

        if filename == "ggml-model-q4_0.bin":
            os.rename(
                "/usr/src/app/weights/ggml-model-q4_0.bin", f"/usr/src/app/weights/ggml-alpaca-{model}-q4_0.bin"
            )


if __name__ == "__main__":
    args = parse_args()

    download_models(args.model)

    print("Converting models to the current format")
    convert_all("/usr/src/app/weights", "/usr/src/app/weights/tokenizer.model")
