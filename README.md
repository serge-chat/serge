# Serge - LLaMA made easy 🦙

![License](https://img.shields.io/github/license/serge-chat/serge)
[![Discord](https://img.shields.io/discord/1088427963801948201?label=Discord)](https://discord.gg/62Hc6FEYQH)

Serge is a chat interface crafted with [llama.cpp](https://github.com/ggerganov/llama.cpp) for running Alpaca models. No API keys, entirely self-hosted!

- 🌐 **SvelteKit** frontend
- 💾 **Redis** for storing chat history & parameters
- ⚙️ **FastAPI + LangChain** for the API, wrapping calls to [llama.cpp](https://github.com/ggerganov/llama.cpp) using the [python bindings](https://github.com/abetlen/llama-cpp-python)

🎥 Demo:

[demo.webm](https://user-images.githubusercontent.com/25119303/226897188-914a6662-8c26-472c-96bd-f51fc020abf6.webm)

## ⚡️ Quick start

🐳 Docker:
```bash
docker run -d \
    --name serge \
    -v weights:/usr/src/app/weights \
    -v datadb:/data/db/ \
    -p 8008:8008 \
    ghcr.io/serge-chat/serge:latest
```

🐙 Docker Compose:
```yaml
services:
  serge:
    image: ghcr.io/serge-chat/serge:latest
    container_name: serge
    restart: unless-stopped
    ports:
      - 8008:8008
    volumes:
      - weights:/usr/src/app/weights
      - datadb:/data/db/

volumes:
  weights:
  datadb:
```

Then, just visit http://localhost:8008/, You can find the API documentation at http://localhost:8008/api/docs

## 🖥️ Windows Setup

Ensure you have Docker Desktop installed, WSL2 configured, and enough free RAM to run models. 

## ☁️ Kubernetes & Docker Compose Setup

Instructions for setting up Serge on Kubernetes can be found in the [wiki](https://github.com/serge-chat/serge/wiki/Integrating-Serge-in-your-orchestration#kubernetes-example).

## 🧠 Supported Models

We currently support the following models:

- Airoboros 🎈
  - Airoboros-7B
  - Airoboros-13B
  - Airoboros-30B
- Alpaca 🦙
  - Alpaca-LoRA-65B
  - GPT4-Alpaca-LoRA-30B
- Chronos 🌑
  - Chronos-13B
  - Chronos-33B
  - Chronos-Hermes-13B
- GPT4All 🌍
  - GPT4All-13B
- Guanaco 🦙
  - Guanaco-7B
  - Guanaco-13B
  - Guanaco-33B
  - Guanaco-65B
- Koala 🐨
  - Koala-7B
  - Koala-13B
- Llama 🦙
  - FinLlama-33B
  - Llama-Supercot-30B
- Lazarus 💀
  - Lazarus-30B
- Nous 🧠
  - Nous-Hermes-13B
- OpenAssistant 🎙️
  - OpenAssistant-30B
- Samantha 👩
  - Samantha-7B
  - Samantha-13B
  - Samantha-33B
- Tulu 🎚
  - Tulu-7B
  - Tulu-13B
  - Tulu-30B
- Vicuna 🦙
  - Stable-Vicuna-13B
  - Vicuna-CoT-7B
  - Vicuna-CoT-13B
  - Vicuna-v1.1-7B
  - Vicuna-v1.1-13B
  - VicUnlocked-30B
  - VicUnlocked-65B
- Wizard 🧙
  - Wizard-Mega-13B
  - Wizard-Vicuna-Uncensored-7B
  - Wizard-Vicuna-Uncensored-13B
  - Wizard-Vicuna-Uncensored-30B
  - WizardLM-30B
  - WizardLM-Uncensored-7B
  - WizardLM-Uncensored-13B
  - WizardLM-Uncensored-30B

Additional weights can be added to the `serge_weights` volume using `docker cp`:

```bash
docker cp ./my_weight.bin serge:/usr/src/app/weights/
```

## ⚠️ Memory Usage

LLaMA will crash if you don't have enough available memory for the model:

| Model    | RAM Required |
|----------|-----------------|
| 7B       | 4.5GB           |
| 7B-q6_K  | 8.03GB          |
| 13B      | 12GB            |
| 13B-q6_K | 13.18GB         |
| 30B      | 20GB            |
| 30B-q6_K | 29.19GB         |

## 💬 Support

Need help? Join our [Discord](https://discord.gg/62Hc6FEYQH)

## 🤝 Contributing

If you discover a bug or have a feature idea, feel free to open an issue or PR.

To run Serge in development mode:

```bash
git clone https://github.com/serge-chat/serge.git
DOCKER_BUILDKIT=1 docker compose -f docker-compose.dev.yml up -d --build
```
