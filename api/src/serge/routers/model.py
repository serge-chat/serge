import asyncio
import os
import shutil


from fastapi import APIRouter, HTTPException
import huggingface_hub
from serge.models.models import Families

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


# Helper functions
async def is_model_installed(model_name: str) -> bool:
    installed_models = await list_of_installed_models()
    return f"{model_name}.bin" in installed_models


async def get_file_size(file_path: str) -> int:
    return os.stat(file_path).st_size


# Handlers
@model_router.get("/all")
async def list_of_all_models():
    installed_models = await list_of_installed_models()
    resp = []

    for model in models_info.keys():
        if await is_model_installed(model):
            available = True
            installed_models.remove(f"{model}.bin")
        else:
            available = False
        resp.append(
            {
                "name": model,
                "size": models_info[model][2],
                "available": available,
                "progress": await download_status(model),
            }
        )
    for model in installed_models:
        resp.append(
            {
                "name": model.replace(".bin", "").lstrip("/"),
                "size": await get_file_size(WEIGHTS + model),
                "available": True,
                "progress": None,
            }
        )
    return resp


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
async def download_model(model_name: str):
    if model_name not in models_info:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        # Download file, and resume broken downloads
        model_repo, filename, _ = models_info[model_name]
        model_path = WEIGHTS + f"{model_name}.bin"
        await asyncio.to_thread(
            huggingface_hub.hf_hub_download, repo_id=model_repo, filename=filename, local_dir=WEIGHTS, cache_dir=WEIGHTS, resume_download=True
        )
        # Rename file
        os.rename(os.path.join(WEIGHTS, filename), os.path.join(WEIGHTS, model_path))
        return {"message": f"Model {model_name} downloaded"}
    except Exception as e:
        # Handle exceptions, possibly log them
        raise HTTPException(status_code=500, detail=f"Error downloading model: {str(e)}")


@model_router.get("/{model_name}/download/status")
async def download_status(model_name: str):
    if model_name not in models_info:
        raise HTTPException(status_code=404, detail="Model not found")

    filesize = models_info[model_name][2]
    model_repo, _, _ = models_info[model_name]

    # Construct the path to the blobs directory
    blobs_dir = os.path.join(WEIGHTS, f"models--{model_repo.replace('/', '--')}", "blobs")

    # Check for the .incomplete file in the blobs directory
    if os.path.exists(os.path.join(WEIGHTS, f"{model_name}.bin")):
        currentsize = os.path.getsize(os.path.join(WEIGHTS, f"{model_name}.bin"))
        return min(round(currentsize / filesize * 100, 1), 100)
    elif os.path.exists(blobs_dir):
        for file in os.listdir(blobs_dir):
            if file.endswith(".incomplete"):
                incomplete_file_path = os.path.join(blobs_dir, file)
                # Check if the .incomplete file exists and calculate the download status
                if os.path.exists(incomplete_file_path):
                    currentsize = os.path.getsize(incomplete_file_path)
                    return min(round(currentsize / filesize * 100, 1), 100)
    return 0


@model_router.delete("/{model_name}")
async def delete_model(model_name: str):
    if model_name + ".bin" not in await list_of_installed_models():
        raise HTTPException(status_code=404, detail="Model not found")

    model_repo, _, _ = models_info.get(model_name, (None, None, None))
    if model_repo is None:
        raise HTTPException(status_code=404, detail="Model info not found")

    # Remove link to model file
    try:
        os.remove(os.path.join(WEIGHTS, f"{model_name}.bin"))
    except OSError as e:
        print(f"Error removing model file: {e}")

    # Remove lock file
    try:
        shutil.rmtree(os.path.join(WEIGHTS, ".locks", f"models--{model_repo.replace('/', '--')}"))
    except OSError as e:
        print(f"Error removing lock directory: {e}")

    # Remove cache directory
    try:
        shutil.rmtree(os.path.join(WEIGHTS, f"models--{model_repo.replace('/', '--')}"))
    except OSError as e:
        print(f"Error removing cache directory: {e}")

    return {"message": f"Model {model_name} deleted"}
