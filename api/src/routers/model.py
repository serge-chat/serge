from fastapi import APIRouter

chat_router = APIRouter(
    prefix="/model",
    tags=["model"],
)
