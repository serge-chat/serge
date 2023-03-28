from fastapi import HTTPException, status
from .utils.convert import convert_all
import anyio
import os

MODEL_IS_READY: bool = False


def dep_models_ready() -> list[str]:
    """
    FastAPI dependency that checks if models are ready.

    Returns a list of available models
    """
    if MODEL_IS_READY is False:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "models are not ready"
            }
        )

    files = os.listdir("/usr/src/app/weights")
    files = list(filter(lambda x: x.endswith(".bin"), files))
    return files


async def convert_model_files():
    global MODEL_IS_READY
    await anyio.to_thread.run_sync(convert_all, "/usr/src/app/weights/", "/usr/src/app/weights/tokenizer.model")
    MODEL_IS_READY = True
