import json
from pathlib import Path
import requests
from huggingface_hub import hf_hub_url
import pytest


def load_model_data(file_path):
    with open(file_path, "r") as models_file:
        return json.load(models_file)


def flatten_model_data(families):
    for family in families:
        for model in family["models"]:
            for file in model["files"]:
                yield model["repo"], file["filename"]


def check_model_availability(repo, filename):
    url = hf_hub_url(repo, filename, repo_type="model", revision="main")
    response = requests.head(url)
    if response.ok:
        return True
    else:
        return False


test_dir = Path(__file__).parent
model_data = load_model_data(test_dir.parent / "src/serge/data/models.json")
checks = list(flatten_model_data(model_data))


@pytest.mark.parametrize("repo,filename", checks)
def test_model_available(repo, filename):
    assert check_model_availability(repo, filename), f"Model {repo}/{filename} not available"
