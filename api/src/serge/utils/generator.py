import asyncio, subprocess
from asyncio.subprocess import Process
import signal
from enum import Enum
from pydantic import BaseModel

from serge.models.chat import Chat, ChatParameters
from typing import Optional

class Status(str, Enum):
    LOADING = "loading"
    IDLE = "idle"
    GENERATING = "generating"
    STOP = "stopping"
    KILLED = "killed"

class Generator(BaseModel):
    user_prompt: str = "Question: "
    process: Optional[type[Process]] = None
    status: Status = Status.IDLE
    id: str = None

    def interrupt(self):
        pass

    async def load_model(self, chat: Chat):
        # kill model in case it was running
        await self._kill()

        # fetch the chat parameters
        await chat.fetch_link(Chat.parameters)

        params = chat.parameters
        await params.fetch_all_links()

        # turn the potential chat history into the initial prompt to feed the model
        init_prompt = self._get_init_prompt(chat)

        args = (
            "llama",
            "--model",
            "/usr/src/app/weights/" + params.model + ".bin",
            "-i",
            "-r",
            init_prompt,
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
            self.user_prompt,
            "--n_parts",
            "1",
            "--interactive-first"
        )

        
        # assign the id property to the chat.id so we know which chat is currently running in the process
        self.id = chat.id

        # create the llama process
        self.process = await asyncio.create_subprocess_exec(
            *args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        # set status to idle so the other methods know to start generating
        self.status = Status.IDLE


    async def _generate_until(self, end_of_text:Optional[str]):
        """
        Used to generate text until a certain string is found in the output
        """

        CHUNK_SIZE = 64 # used for determining how much to read from the process at a time
        text = ""

        if self.status != Status.IDLE:
            raise ValueError("Generator is not idle")
        
        # set status to generating so the model knows
        self.status = Status.GENERATING
        
        while True:
            chunk = await self.process.stdout.read(CHUNK_SIZE)

            if self.status == Status.STOP:
                self.process.send_signal(signal.SIGINT)
                self.status = Status.IDLE
                return
            
            if not chunk:
                return_code = await self.process.wait()

                if return_code != 0:
                    error_output = await self.process.stderr.read()
                    raise ValueError(f"RETURN CODE {return_code}\n\n"+error_output.decode("utf-8"))
                else:
                    return

            try:
                chunk = chunk.decode("utf-8")
                text += chunk
                yield chunk
            except UnicodeDecodeError:
                return
        
            if end_of_text!=None and end_of_text in text:
                return
    
    async def _kill(self):
        if self.process != None:
            self.process.kill()
            await self.process.wait()
            self.process = None

        self.status = Status.KILLED
        return True
    
    async def generate(self, question: str):
        print("generating", question, self.status)

        # if self.status == Status.KILLED:
        #     raise ValueError("Generator is killed")

        # self.status = Status.STOP

        # the _generate_until method will set the status to IDLE when it sends the ctrl+c signal
        # while self.status != Status.IDLE:
        #     await asyncio.sleep(0.05)
            
        self.process.stdin.communicate(question.encode("utf-8"))

        async for chunk in self._generate_until(self.user_prompt):
            print(chunk)
            yield chunk

    def _get_init_prompt(self, chat: Chat):
        prompt = chat.parameters.init_prompt + "\\\n\\\n"
        
        if chat.questions != None:
            for question in chat.questions:
                if question.error != None: # skip errored out prompts
                    continue
                prompt += "### Question:\\\n" + question.question + "\\\n"
                prompt += "### Answer:\\\n" + question.answer + "\\\n"

        prompt += "### Question:\\\n"
        return prompt
