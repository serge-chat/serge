import asyncio
import os
import shutil

import aiohttp

from fastapi import APIRouter, HTTPException
from huggingface_hub import hf_hub_url
from serge.models.models import Families

from pathlib import Path

model_router = APIRouter(
    prefix="/model",
    tags=["model"],
)

active_downloads = {}

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
    return any(file_name == f"{model_name}.bin" and not file_name.startswith(".") for file_name in installed_models)


async def get_file_size(file_path: str) -> int:
    return os.stat(file_path).st_size


async def cleanup_model_resources(model_name: str):
    model_repo, _, _ = models_info.get(model_name, (None, None, None))
    if not model_repo:
        print(f"No model repo found for {model_name}, cleanup may be incomplete.")
        return

    temp_model_path = os.path.join(WEIGHTS, f".{model_name}.bin")
    lock_dir = os.path.join(WEIGHTS, ".locks", f"models--{model_repo.replace('/', '--')}")
    cache_dir = os.path.join(WEIGHTS, f"models--{model_repo.replace('/', '--')}")

    # Try to cleanup temporary file if it exists
    if os.path.exists(temp_model_path):
        try:
            os.remove(temp_model_path)
        except OSError as e:
            print(f"Error removing temporary file for {model_name}: {e}")

    # Remove lock file if it exists
    if os.path.exists(lock_dir):
        try:
            shutil.rmtree(lock_dir)
        except OSError as e:
            print(f"Error removing lock directory for {model_name}: {e}")

    # Remove cache directory if it exists
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
        except OSError as e:
            print(f"Error removing cache directory for {model_name}: {e}")


async def download_file(session: aiohttp.ClientSession, url: str, path: str) -> None:
    async with session.get(url) as response:
        if response.status != 200:
            raise HTTPException(status_code=500, detail="Error downloading model")

        # Write response content to file asynchronously
        with open(path, "wb") as f:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)


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
                "progress": 100.0,
            }
        )
    return resp


@model_router.get("/installed")
async def list_of_installed_models():
    # Iterate through the WEIGHTS directory and return filenames that end with .bin and do not start with a dot
    files = [
        os.path.join(model_location.replace(WEIGHTS, "").lstrip("/"), bin_file)
        for model_location, _, filenames in os.walk(WEIGHTS)
        for bin_file in filenames
        if bin_file.endswith(".bin") and not bin_file.startswith(".")
    ]
    return files


@model_router.post("/{model_name}/download")
async def download_model(model_name: str):
    if model_name not in models_info:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        model_repo, filename, _ = models_info[model_name]
        model_url = hf_hub_url(repo_id=model_repo, filename=filename)
        temp_model_path = os.path.join(WEIGHTS, f".{model_name}.bin")
        model_path = os.path.join(WEIGHTS, f"{model_name}.bin")

        # Create an aiohttp session with timeout settings
        timeout = aiohttp.ClientTimeout(total=None, connect=300, sock_read=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Start the download and add to active_downloads
            download_task = asyncio.create_task(download_file(session, model_url, temp_model_path))
            active_downloads[model_name] = download_task
            await download_task

        # Rename the dotfile to its final name
        os.rename(temp_model_path, model_path)

        # Remove the entry from active_downloads after successful download
        active_downloads.pop(model_name, None)

        return {"message": f"Model {model_name} downloaded"}
    except asyncio.CancelledError:
        await cleanup_model_resources(model_name)
        raise HTTPException(status_code=200, detail="Download cancelled")
    except Exception as exc:
        await cleanup_model_resources(model_name)
        raise HTTPException(status_code=500, detail=f"Error downloading model: {exc}")


@model_router.post("/{model_name}/download/cancel")
async def cancel_download(model_name: str):
    try:
        task = active_downloads.get(model_name)
        if not task:
            raise HTTPException(status_code=404, detail="No active download for this model")

        # Remove the entry from active downloads after cancellation
        task.cancel()

        # Remove entry from active downloads
        active_downloads.pop(model_name, None)

        # Wait for the task to be cancelled
        try:
            # Wait for the task to respond to cancellation
            print(f"Waiting for download for {model_name} to be cancelled")
            await task
        except asyncio.CancelledError:
            # Handle the expected cancellation exception
            pass

        # Cleanup resources
        await cleanup_model_resources(model_name)

        print(f"Download for {model_name} cancelled")
        return {"message": f"Download for {model_name} cancelled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling model download: {str(e)}")


@model_router.get("/{model_name}/download/status")
async def download_status(model_name: str):
    if model_name not in models_info:
        raise HTTPException(status_code=404, detail="Model not found")

    filesize = models_info[model_name][2]
    model_repo, _, _ = models_info[model_name]

    # Construct the path to the blobs directory
    temp_model_path = os.path.join(WEIGHTS, f".{model_name}.bin")
    model_path = os.path.join(WEIGHTS, f"{model_name}.bin")

    # Check if the model is currently being downloaded
    task = active_downloads.get(model_name)

    if os.path.exists(model_path):
        currentsize = os.path.getsize(model_path)
        progress = min(round(currentsize / filesize * 100, 1), 100)
        return progress
    elif task and not task.done():
        # If the task is still running, check for incomplete files
        if os.path.exists(temp_model_path):
            currentsize = os.path.getsize(temp_model_path)
            return min(round(currentsize / filesize * 100, 1), 100)
        # If temp_model_path doesn't exist, the download is likely just starting, progress is 0
        return 0
    else:
        # No active download and the file does not exist
        return None


@model_router.delete("/{model_name}")
async def delete_model(model_name: str):
    if f"{model_name}.bin" not in await list_of_installed_models():
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        os.remove(os.path.join(WEIGHTS, f"{model_name}.bin"))
    except OSError as e:
        print(f"Error removing model file: {e}")

    await cleanup_model_resources(model_name)

    return {"message": f"Model {model_name} deleted"}
