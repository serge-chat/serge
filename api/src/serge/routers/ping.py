from fastapi import APIRouter

ping_router = APIRouter(
    prefix="/ping",
    tags=["ping"],
)


@app.get("/")
def pong():
    return "pong!"