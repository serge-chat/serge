import re


from langchain.memory import RedisChatMessageHistory
from loguru import logger


def get_prompt(history: RedisChatMessageHistory, params):
    """
    Get the prompt for the LLM from the chat history.
    """

    def tokenize_content(content):
        split_content = list(filter(None, re.split("([^\\n\.\?!]+[\\n\.\?! ]+)", content)))
        split_content.reverse()
        return split_content

    def sum_prompts_lengths(prompts):
        prompt_length = 0
        for s in prompts:
            prompt_length += len(s)
        return prompt_length

    dupes = {}
    prompts = []
    messages = history.messages.copy()
    messages.reverse()
    for message in messages:
        if message.content in dupes:
            continue
        dupes[message.content] = True

        instruction = ""
        match message.type:
            case "human":
                instruction = "### Instruction: "
            case "ai":
                instruction = "### Response: "
            # case "system":
            #     instruction = "### System: "
            case _:
                continue

        stop = False
        next_prompt = ""
        tokens = tokenize_content(message.content)
        prompt_length = sum_prompts_lengths(prompts)
        for token in tokens:
            if prompt_length + len(next_prompt) + len(token) < params.n_ctx:
                next_prompt = token + next_prompt
            else:
                stop = True
        if len(next_prompt) > 0:
            prompts.append(f"{instruction + next_prompt}\n")
        if stop:
            break

    message_prompt = ""
    prompts.reverse()
    for next_prompt in prompts:
        message_prompt += next_prompt

    final_prompt = f"{params.init_prompt}\n{message_prompt[:params.n_ctx]}"
    logger.debug(final_prompt)
    return final_prompt
