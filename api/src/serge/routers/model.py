from fastapi import APIRouter, HTTPException

from serge.utils.convert import convert_one_file
import huggingface_hub
import os
import urllib.request

model_router = APIRouter(
    prefix="/model",
    tags=["model"],
)

models_info = {
    "7B": [
        "nsarrazin/alpaca",
        "alpaca-7B-ggml/ggml-model-q4_0.bin", 
        4.20E9,
        ],
    "7B-native": [
        "nsarrazin/alpaca", 
        "alpaca-native-7B-ggml/ggml-model-q4_0.bin", 
        4.20E9,
        ],
    "13B": [
        "nsarrazin/alpaca", 
        "alpaca-13B-ggml/ggml-model-q4_0.bin", 
        8.13E9,
        ],
    "30B": [
        "nsarrazin/alpaca", 
        "alpaca-30B-ggml/ggml-model-q4_0.bin", 
        20.2E9,
        ],
    }

WEIGHTS = "/usr/src/app/weights/"

@model_router.get("/all")
async def list_of_all_models():
    res = []
    for model in models_info.keys():
        
        progress = await download_status(model)
        
        res.append({
            "name": model,
            "size": models_info[model][2],
            "available": model+".bin" in await list_of_installed_models(),
            "progress" : progress,
        })
    
    return res

@model_router.get("/downloadable")
async def list_of_downloadable_models():
    files = os.listdir(WEIGHTS)
    files = list(filter(lambda x: x.endswith(".bin"), files))

    installed_models = [i.rstrip(".bin") for i in files]
    
    return list(filter(lambda x: x not in installed_models, models_info.keys()))

@model_router.get("/installed")
async def list_of_installed_models():
    files = os.listdir(WEIGHTS)
    files = list(filter(lambda x: x.endswith(".bin"), files))

    return files 


@model_router.post("/{model_name}/download")
def download_model(model_name: str):
    models = list(models_info.keys())
    if model_name not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if not os.path.exists(WEIGHTS+ "tokenizer.model"):
        print("Downloading tokenizer...")
        url = huggingface_hub.hf_hub_url("nsarrazin/alpaca", "alpaca-7B-ggml/tokenizer.model", repo_type="model", revision="main")
        urllib.request.urlretrieve(url, WEIGHTS+"tokenizer.model")

    
    repo_id, filename,_ = models_info[model_name]

    print(f"Downloading {model_name} model from {repo_id}...")
    url = huggingface_hub.hf_hub_url(repo_id, filename, repo_type="model", revision="main")
    urllib.request.urlretrieve(url, WEIGHTS+f"{model_name}.bin.tmp")

    os.rename(WEIGHTS+f"{model_name}.bin.tmp", WEIGHTS+f"{model_name}.bin")
    convert_one_file(WEIGHTS+ "f{model_name}.bin", WEIGHTS + f"tokenizer.model")

    return {"message": f"Model {model_name} downloaded"}


@model_router.get("/{model_name}/download/status")
async def download_status(model_name: str):
    models = list(models_info.keys())

    if model_name not in models:
        raise HTTPException(status_code=404, detail="Model not found")

    filesize = models_info[model_name][2]

    bin_path = WEIGHTS+f"{model_name}.bin.tmp"

    if os.path.exists(bin_path):
        currentsize = os.path.getsize(bin_path)
        return min(round(currentsize / filesize*100, 1), 100)        
    return None