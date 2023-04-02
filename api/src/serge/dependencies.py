from .utils.convert import convert_all
import anyio, redis


async def convert_model_files():
    await anyio.to_thread.run_sync(
        convert_all, "/usr/src/app/weights/", "/usr/src/app/weights/tokenizer.model"
    )
