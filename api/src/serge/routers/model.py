from fastapi import APIRouter

model_router = APIRouter(
    prefix="/model",
    tags=["model"],
)
