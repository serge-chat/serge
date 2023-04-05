from pydantic import BaseModel
from serge.worker.worker import Worker
from serge.utils.initiate_database import initiate_database
from typing import Optional

import asyncio
import redis
import sys

from loguru import logger

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="DEBUG"
)


MAX_ACTIVE_CONVERSATIONS = 4

class Orchestrator(BaseModel):
    workers: dict[str, type[Worker]] = {}
    client: Optional[redis.Redis] = None
    kill_sig: bool = False

    class Config:
        arbitrary_types_allowed = True

    async def start(self):
        # mongoDB connection
        logger.debug("Connecting to MongoDB")
        await initiate_database()

        # redis connection
        logger.debug("Setting up redis connection")
        self.client = redis.Redis()
        logger.debug(f"Redis Ping successful: {self.client.ping()}")

        logger.debug("Cleaning up past queues")
        self.client.delete("load_queue")
        self.client.delete("unload_queue")
        self.client.delete("loaded_chats")

        self.client.lpush("load_queue", "")
        self.client.lpush("unload_queue", "")

    async def stop(self):
        await self.client.close()

        for worker in self.workers.values():
            await worker.kill()

    async def run(self):
        await self.start()

        logger.debug("Beginning main loop")
        try:
            while True:
                await asyncio.sleep(0.05)
                # check the queue for new chats to load
                while self.client.llen("load_queue") > 1:
                    
                    # check if there are more than the maximum allowed amount of active conversations
                    if len(self.workers) >= MAX_ACTIVE_CONVERSATIONS:
                        logger.info("Too many active conversations, getting rid of the earliest activated conversation...")
                        # pop the first chat that was added
                        key_to_delete = next(iter(self.workers))
                        await self.remove_worker(key_to_delete)
                        self.client.srem("loaded_chats", chat_id)

                    
                    # fetch the next chat to load, and wait for it to load
                    chat_id:bytes = self.client.lindex("load_queue", 1)
                    logger.debug(
                        f"Found element{chat_id} in load_queue, adding worker..."
                    )
                    await self.add_worker(chat_id.decode())

                    logger.debug(
                        f"Removing element from load queue, and adding it to loaded chats"
                    )

                    # remove the chat from the queue and add it to the loaded chats set
                    self.client.lpop("load_queue", 1)
                    self.client.sadd("loaded_chats", chat_id)

                while self.client.llen("unload_queue") > 1:
                    chat_id:bytes = self.client.lindex("unload_queue", 1)
                    logger.debug(f"Found element {chat_id} in unload_queue, removing worker...")
                    
                    await self.remove_worker(chat_id.decode())

                    self.client.lpop("unload_queue", 1)
                    self.client.srem("loaded_chats", chat_id)

                # kill signal to get out of loop
                if self.kill_sig:
                    break

        except Exception as e:
            raise e
        finally:
            # when we get out of the loop somehow, properly close connections and kill all workers
            await self.stop()

    async def add_worker(self, chat_id: str):
        worker = await Worker.create(chat_id)
        self.workers[chat_id] = worker

    async def remove_worker(self, chat_id: str):
        try:
            worker = self.workers[chat_id]
            worker.loop_task.cancel()
            del self.workers[chat_id]
        except KeyError:
            logger.info(f"Could not delete worker {chat_id}. Worker not found.")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run())
