from pydantic import BaseModel
from serge.worker.worker import Worker
from serge.utils.initiate_database import initiate_database
from typing import Optional

import asyncio
import redis

from typing import Optional, List


class Orchestrator(BaseModel):
    workers: dict[str, type[Worker]] = {}
    client: Optional[redis.Redis] = None
    kill_sig: bool = False

    class Config:
        arbitrary_types_allowed = True

    async def start(self):
        # mongoDB connection
        await initiate_database()

        # redis connection
        self.client = redis.Redis()
        print(f"Ping successful: {self.client.ping()}")

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

        try:
            while True:
                await asyncio.sleep(0.05)
                # check the queue for new chats to load
                while self.client.llen("load_queue") > 1:
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
