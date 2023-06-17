import os
import json
import urllib.request

import huggingface_hub
from fastapi import APIRouter, HTTPException

from serge.models.models import Families
from serge.utils.convert import convert_one_file
from serge.utils.migrate import migrate

from pathlib import Path

model_router = APIRouter(
    prefix="/model",
    tags=["model"],
)

WEIGHTS = "/usr/src/app/weights/"

models_file_path = Path(__file__).parent.parent / "data" / "models.json"
families = Families.parse_file(models_file_path)

models_info = {}
for family in families.__root__:
    for model in family.models:
        for file in model.files:
            models_info[model.name] = (
                model.repo,
                file.filename,
                file.disk_space,
            )


@model_router.get("/all")
async def list_of_all_models():
    res = []
    installed_models = await list_of_installed_models()
    for model in models_info.keys():
        progress = await download_status(model)
        if f"{model}.bin" in installed_models:
            available = True
            # if model exists in WEIGHTS directory remove it from the list
            installed_models.remove(f"{model}.bin")
        else:
            available = False
        res.append(
            {
                "name": model,
                "size": models_info[model][2],
                "available": available,
                "progress": progress,
            }
        )
    # append the rest of the models
    for model in installed_models:
        # .bin is removed for compatibility with generate.py
        res.append(
            {
                "name": model.replace(".bin", "").lstrip("/"),
                "size": os.stat(WEIGHTS + model).st_size,
                "available": True,
                "progress": None,
            }
        )

    return res


@model_router.get("/downloadable")
async def list_of_downloadable_models():
    files = os.listdir(WEIGHTS)
    files = list(filter(lambda x: x.endswith(".bin"), files))

    installed_models = [i.rstrip(".bin") for i in files]

    return list(filter(lambda x: x not in installed_models, models_info.keys()))


@model_router.get("/installed")
async def list_of_installed_models():
    # after iterating through the WEIGHTS directory, return location and filename
    files = [
        model_location.replace(WEIGHTS, "") + "/" + bin_file
        for model_location, directory, filenames in os.walk(WEIGHTS)
        for bin_file in filenames
        if os.path.splitext(bin_file)[1] == ".bin"
    ]
    files = [i.lstrip("/") for i in files]
    return files


@model_router.post("/{model_name}/download")
def download_model(model_name: str):
    models = list(models_info.keys())
    if model_name not in models:
        raise HTTPException(status_code=404, detail="Model not found")

    if not os.path.exists(WEIGHTS + "tokenizer.model"):
        print("Downloading tokenizer...")
        url = huggingface_hub.hf_hub_url(
            "nsarrazin/alpaca",
            "alpaca-7B-ggml/tokenizer.model",
            repo_type="model",
            revision="main",
        )
        urllib.request.urlretrieve(url, WEIGHTS + "tokenizer.model")

    repo_id, filename, _ = models_info[model_name]

    print(f"Downloading {model_name} model from {repo_id}...")
    url = huggingface_hub.hf_hub_url(
        repo_id, filename, repo_type="model", revision="main"
    )
    urllib.request.urlretrieve(url, WEIGHTS + f"{model_name}.bin.tmp")

    os.rename(WEIGHTS + f"{model_name}.bin.tmp", WEIGHTS + f"{model_name}.bin")
    convert_one_file(WEIGHTS + f"{model_name}.bin", WEIGHTS + "tokenizer.model")
    migrate(WEIGHTS + f"{model_name}.bin")

    return {"message": f"Model {model_name} downloaded"}


@model_router.get("/{model_name}/download/status")
async def download_status(model_name: str):
    models = list(models_info.keys())

    if model_name not in models:
        raise HTTPException(status_code=404, detail="Model not found")

    filesize = models_info[model_name][2]

    bin_path = WEIGHTS + f"{model_name}.bin.tmp"

    if os.path.exists(bin_path):
        currentsize = os.path.getsize(bin_path)
        return min(round(currentsize / filesize * 100, 1), 100)
    return None


@model_router.delete("/{model_name}")
async def delete_model(model_name: str):
    if model_name + ".bin" not in await list_of_installed_models():
        raise HTTPException(status_code=404, detail="Model not found")

    if os.path.exists(WEIGHTS + f"{model_name}.bin"):
        os.remove(WEIGHTS + f"{model_name}.bin")
        return {"message": f"Model {model_name} deleted"}

    raise HTTPException(status_code=404, detail="Model file not found")
