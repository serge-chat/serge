import json
from pathlib import Path

import huggingface_hub
import pytest
import requests

# this test file specifically doesn't start with test_* so it's not picked up by pytest

test_dir = Path(__file__).parent
with open(test_dir.parent / "src/serge/data/models.json", "r") as models_file:
    families = json.load(models_file)

# generate list of checks
checks = []
for family in families:
    for model in family["models"]:
        for file in model["files"]:
            checks.append((model["repo"], file["filename"]))


@pytest.mark.parametrize("repo,filename", checks)
def test_model_available(repo, filename):
    url = huggingface_hub.hf_hub_url(repo, filename, repo_type="model", revision="main")
    r = requests.head(url)
    assert r.ok, f"Model {repo}/{filename} not available"
