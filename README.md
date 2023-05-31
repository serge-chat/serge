# Serge - LLaMA made easy 🦙

![License](https://img.shields.io/github/license/nsarrazin/serge)
[![Discord](https://img.shields.io/discord/1088427963801948201?label=Discord)](https://discord.gg/62Hc6FEYQH)

A chat interface based on [llama.cpp](https://github.com/ggerganov/llama.cpp) for running Alpaca models. Entirely self-hosted, no API keys needed. Fits on 4GB of RAM and runs on the CPU.

- **SvelteKit** frontend
- **Redis** for storing chat history & parameters
- **FastAPI + langchain** for the API, wrapping calls to [llama.cpp](https://github.com/ggerganov/llama.cpp) using the [python bindings](https://github.com/abetlen/llama-cpp-python)

[demo.webm](https://user-images.githubusercontent.com/25119303/226897188-914a6662-8c26-472c-96bd-f51fc020abf6.webm)

## Getting started

Setting up Serge is very easy. Starting it up can be done in a single command:

```
docker run -d -v weights:/usr/src/app/weights -v datadb:/data/db/ -p 8008:8008 ghcr.io/nsarrazin/serge:latest
```

Then just go to http://localhost:8008/ and you're good to go!

The API documentation can be found at http://localhost:8008/api/docs

#### Windows

Make sure you have docker desktop installed, WSL2 configured and enough free RAM to run models. (see below)

#### Kubernetes & docker compose

Setting up Serge on Kubernetes or docker compose can be found in the wiki: https://github.com/nsarrazin/serge/wiki/Integrating-Serge-in-your-orchestration#kubernetes-example

#### Web3 - Akash Network (AKT)

Deploy Serge effortlessly on the [Akash.Network](https://akash.network) via Cloudmos, a transparent and secure decentralized cloud computing platform. 

[<img src="https://github.com/88plug/serge/blob/main/Cloudmos.png?raw=true">](https://deploy.cloudmos.io/templates/akash-network-awesome-akash-serge/)

1. Follow the [Get Started](https://deploy.cloudmos.io/get-started/wallet) guide to set up Cloudmos.
2. Utilize the Serge template for a new deployment. 
3. After deployment, access the web interface via the unique URI(s) link found on the `Deployment detail > Leases` tab. 

## Models

Currently the following models are supported:

- GPT4-Alpaca-LoRA-30B
- Alpaca-LoRA-65B
- OpenAssistant-30B
- GPT4All-13B
- Stable-Vicuna-13B
- Guanaco-7B
- Guanaco-13B
- Guanaco-33B
- Guanaco-65B

If you have existing weights from another project you can add them to the `serge_weights` volume using `docker cp`.

### :warning: A note on _memory usage_

LLaMA will just crash if you don't have enough available memory for your model.

- 7B requires about 4.5GB of free RAM
- 13B requires about 12GB free
- 30B requires about 20GB free


## Support

Feel free to join the discord if you need help with the setup: https://discord.gg/62Hc6FEYQH

## Contributing

Serge is always open for contributions! If you catch a bug or have a feature idea, feel free to open an issue or a PR.

If you want to run Serge in development mode (with hot-module reloading for svelte & autoreload for FastAPI) you can do so like this:

```
git clone https://github.com/nsarrazin/serge.git
DOCKER_BUILDKIT=1 docker compose -f docker-compose.dev.yml up -d --build
```

You can test the production image with

```
DOCKER_BUILDKIT=1 docker compose up -d --build
```

## What's next

- [x] Front-end to interface with the API
- [x] Pass model parameters when creating a chat
- [x] Manager for model files
- [ ] Support for other models
- [ ] LangChain integration
- [ ] User profiles & authentication

And a lot more!
