# Serge - LLaMa made easy 🦙

![License](https://img.shields.io/github/license/nsarrazin/serge)
[![Discord](https://img.shields.io/discord/1088427963801948201?label=Discord)](https://discord.gg/62Hc6FEYQH)

A chat interface based on `llama.cpp` for running Alpaca models. Entirely self-hosted, no API keys needed. Fits on 4GB of RAM and runs on the CPU.

- **SvelteKit** frontend
- **MongoDB** for storing chat history & parameters
- **FastAPI + beanie** for the API, wrapping calls to `llama.cpp`

[demo.webm](https://user-images.githubusercontent.com/25119303/226897188-914a6662-8c26-472c-96bd-f51fc020abf6.webm)

## Getting started

Setting up Serge is very easy. TLDR for running it with Alpaca 7B:

```
git clone https://github.com/nsarrazin/serge.git
cd serge

docker compose -f docker-compose.prebuilt.yml up -d
docker compose exec serge python3 /usr/src/app/api/utils/download.py tokenizer 7B
```

Or if you prefer to build the container from source:

```
git clone https://github.com/nsarrazin/serge.git
cd serge

docker compose up -d
docker compose exec serge python3 /usr/src/app/api/utils/download.py tokenizer 7B
```

#### Windows

:warning: For cloning on windows, use `git clone https://github.com/nsarrazin/serge.git --config core.autocrlf=input`.

Make sure you have docker desktop installed, WSL2 configured and enough free RAM to run models. (see below)

#### Kubernetes

Setting up Serge on Kubernetes can be found in the wiki: https://github.com/nsarrazin/serge/wiki/Integrating-Serge-in-your-orchestration#kubernetes-example

### Using serge

(You can pass `7B 13B 30B` as an argument to the `download.py` script to download multiple models.)

Then just go to http://localhost:8008/ and you're good to go!

The API is available at http://localhost:8008/api/

## Models

Currently only the 7B, 13B and 30B alpaca models are supported. There's a download script for downloading them inside of the container, described above.

If you have existing weights from another project you can add them to the `serge_weights` volume using `docker cp`.

### :warning: A note on _memory usage_

llama will just crash if you don't have enough available memory for your model.

- 7B requires about 4.5GB of free RAM
- 13B requires about 12GB free
- 30B requires about 20GB free

## Support

Feel free to join the discord if you need help with the setup: https://discord.gg/62Hc6FEYQH

## What's next

- [x] Front-end to interface with the API
- [x] Pass model parameters when creating a chat
- [ ] User profiles & authentication
- [ ] Different prompt options
- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.

And a lot more!
