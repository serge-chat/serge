from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends

from serge.dependencies import dep_models_ready

model_router = APIRouter(
    prefix="/model",
    tags=["model"],
)

@model_router.get("/")
def list_of_installed_models(
        models: Annotated[list[str], Depends(dep_models_ready)]
):
    return models

