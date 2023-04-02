from pydantic import BaseModel
from typing import Optional
from asyncio.subprocess import Process

from serge.models.chat import Chat, Question
import asyncio 
import subprocess
import redis

CHUNK_SIZE = 64
SLEEP = 0.01
class Worker(BaseModel):
    loop_task: Optional[asyncio.Task] = None
    subprocess: Optional[Process] = None

    client: Optional[TypeVar("Redis")] = None
    chat: Optional[Chat] = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    async def create(cls, chat_id: str):
        logger.debug("Creating a Worker")
        chat = await Chat.get(chat_id)

        if chat == None:
            raise ValueError("Chat document not found while creating the worker thread")

        worker = cls(subprocess=None, client=redis.Redis(), chat=chat)

        logger.debug("Starting worker process")
        await worker._start_process()

        logger.debug("Adding event loop to new thread")
        worker.loop_task = asyncio.create_task(asyncio.to_thread(worker.loop))
        await worker.loop_task
        
        return worker
    
    @property 
    def queue(self):
        return f"questions:{self.chat.id}"
    
    @property
    def stream(self):
        return f"stream:{self.chat.id}"
    
    async def loop(self):        
        try:
            while True:
                await asyncio.sleep(0.05)

                if self.client.llen(self.queue) > 1:
                    question = self.client.lindex(self.queue, -1)
                    print(f"Question: {question}")

                    answer = await self._answer_question(question)
                    self.client.lpop(self.queue, 1)
                    
                    question = await Question(question=question, answer=answer).create()
                    if self.chat.questions is None:
                        self.chat.questions = [question]
                    else:
                        self.chat.questions.append(question)
                    
                    await self.chat.save()

                    print(f"Answer: {answer}")

        except asyncio.CancelledError:
            await self.subprocess.terminate()
            return True

    async def _answer_question(self, question):
        answer = ""
        
        self.subprocess.communicate(input=question.encode("utf-8"))
        self.subprocess.communicate(input=b"\n")

        while True:
            chunk = await self.subprocess.stdout.read(CHUNK_SIZE)

            if not chunk:
                return_code = await self.subprocess.wait()

                if return_code != 0:
                    error_output = await self.subprocess.stderr.read()
                    print(error_output.decode("utf-8"))
                    raise ValueError(f"RETURN CODE {return_code}\n\n"+error_output.decode("utf-8"))
                else:
                    return answer

            try:
                chunk = chunk.decode("utf-8")
                answer += chunk
                await self.client.append(self.stream, chunk)

                if answer.endswith("Question: "):
                    self.client.set(self.stream, "")
                    return answer[:-10]
            except UnicodeDecodeError:
                return answer

    async def _get_start_prompt(self):
        await self.chat.fetch_all_links()
        await self.chat.parameters.fetch_all_links()

        prompt = self.chat.parameters.init_prompt + "\n\n"

        if self.chat.questions != None:
            await self.chat.questions.fetch_all_links()
            for question in self.chat.questions:
                if question.error != None: # skip errored out prompts
                    continue
                prompt += "### Question:\n" + question.question + "\n"
                prompt += "### Answer:\n" + question.answer + "\n"

        prompt += "### Question:\n"
        return prompt

    async def _start_process(self):

        await self.chat.fetch_link(Chat.parameters)
        params = self.chat.parameters
        await params.fetch_all_links()

        prompt = await self._get_start_prompt()

        newprompt = prompt.replace("\n", "\\\n")

        args = (
            "llama",
            "--model",
            "/usr/src/app/weights/" + params.model + ".bin",
            "-i",
            "-r",
            newprompt,
            "--n_predict",
            str(params.max_length),
            "--temp",
            str(params.temperature),
            "--top_k",
            str(params.top_k),
            "--top_p",
            str(params.top_p),
            "--repeat_last_n",
            str(params.repeat_last_n),
            "--repeat_penalty",
            str(params.repeat_penalty),
            "--ctx_size",
            str(params.context_window),
            "--threads",
            str(params.n_threads),
            "--in-prefix",
            "Question: ",
            "--n_parts",
            "1",
            "--interactive-first"
        )

        self.subprocess = await asyncio.create_subprocess_exec(
                        *args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        return True
