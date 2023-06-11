# Serge - LLaMA made easy 🦙

![License](https://img.shields.io/github/license/serge-chat/serge)
[![Discord](https://img.shields.io/discord/1088427963801948201?label=Discord)](https://discord.gg/62Hc6FEYQH)

A chat interface based on [llama.cpp](https://github.com/ggerganov/llama.cpp) for running Alpaca models. Entirely self-hosted, no API keys needed. Fits on 4GB of RAM and runs on the CPU.

- **SvelteKit** frontend
- **Redis** for storing chat history & parameters
- **FastAPI + langchain** for the API, wrapping calls to [llama.cpp](https://github.com/ggerganov/llama.cpp) using the [python bindings](https://github.com/abetlen/llama-cpp-python)

[demo.webm](https://user-images.githubusercontent.com/25119303/226897188-914a6662-8c26-472c-96bd-f51fc020abf6.webm)

## Getting started

Setting up Serge is very easy. Starting it up can be done in a single command:

```
docker run -d \
    --name serge \
    -v weights:/usr/src/app/weights \
    -v datadb:/data/db/ \
    -p 8008:8008 \
    ghcr.io/serge-chat/serge:main
```

Then just go to http://localhost:8008/ and you're good to go!

The API documentation can be found at http://localhost:8008/api/docs

#### Windows

Make sure you have docker desktop installed, WSL2 configured and enough free RAM to run models. (see below)

#### Kubernetes & docker compose

Setting up Serge on Kubernetes or docker compose can be found in the wiki: https://github.com/serge-chat/serge/wiki/Integrating-Serge-in-your-orchestration#kubernetes-example

## Models

Currently the following models are supported:

### Alpaca
- Alpaca-LoRA-65B
- GPT4-Alpaca-LoRA-30B

### GPT4All
- GPT4All-13B

### Guanaco
- Guanaco-7B
- Guanaco-13B
- Guanaco-33B
- Guanaco-65B

### Koala
- Koala-7B
- Koala-13B

### Lazarus
- Lazarus-30B

### Nous
- Nous-Hermes-13B

### OpenAssistant
- OpenAssistant-30B

### Samantha
- Samantha-7B
- Samantha-13B
- Samantha-33B

### Stable
- Stable-Vicuna-13B

### Vicuna
- Vicuna-CoT-7B
- Vicuna-CoT-13B
- Vicuna-v1.1-7B
- Vicuna-v1.1-13B

### Wizard
- Wizard-Mega-13B
- Wizard-Vicuna-Uncensored-7B
- Wizard-Vicuna-Uncensored-13B
- Wizard-Vicuna-Uncensored-30B
- WizardLM-30B
- WizardLM-Uncensored-7B
- WizardLM-Uncensored-13B
- WizardLM-Uncensored-30B

If you have existing weights from another project you can add them to the `serge_weights` volume using `docker cp`.

### :warning: A note on _memory usage_

LLaMA will just crash if you don't have enough available memory for your model.

- 7B requires about 4.5GB of free RAM
- 7B-q6_K requires about 8.03 GB of free RAM
- 13B requires about 12GB free
- 13B-q6_K requires about 13.18 GB free
- 30B requires about 20GB free
- 30B-q6_K requires about 29.19 GB free

## Support

Feel free to join the discord if you need help with the setup: https://discord.gg/62Hc6FEYQH

## Contributing

Serge is always open for contributions! If you catch a bug or have a feature idea, feel free to open an issue or a PR.

If you want to run Serge in development mode (with hot-module reloading for svelte & autoreload for FastAPI) you can do so like this:

```
git clone https://github.com/serge-chat/serge.git
DOCKER_BUILDKIT=1 docker compose -f docker-compose.dev.yml up -d --build
```

You can test the production image with

```
DOCKER_BUILDKIT=1 docker compose up -d --build
```
