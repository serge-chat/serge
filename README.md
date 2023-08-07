# Serge - LLaMA made easy 🦙

![License](https://img.shields.io/github/license/serge-chat/serge)
[![Discord](https://img.shields.io/discord/1088427963801948201?label=Discord)](https://discord.gg/62Hc6FEYQH)

Serge is a chat interface crafted with [llama.cpp](https://github.com/ggerganov/llama.cpp) for running Alpaca models. No API keys, entirely self-hosted!

- 🌐 **SvelteKit** frontend
- 💾 **[Dragonfly](https://github.com/dragonflydb/dragonfly)** for storing chat history & parameters
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

- Alpaca 🦙
  - Alpaca-LoRA-65B
  - GPT4-Alpaca-LoRA-30B
- Chronos 🌑
  - Chronos-13B
  - Chronos-33B
  - Chronos-Hermes-13B
- GPT4All 🌍
  - GPT4All-13B
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
- Orca 🐬
  - Orca-Mini-v2-7B
  - Orca-Mini-v2-13B
  - OpenOrca-Preview1-13B
- Samantha 👩
  - Samantha-7B
  - Samantha-13B
  - Samantha-33B
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
  - WizardLM-Uncensored-7B
  - WizardLM-Uncensored-13B
  - WizardLM-Uncensored-30B

Additional weights can be added to the `serge_weights` volume using `docker cp`:

```bash
docker cp ./my_weight.bin serge:/usr/src/app/weights/
```

## ⚠️ Memory Usage

LLaMA will crash if you don't have enough available memory for the model:

| Model       | Max RAM Required |
|-------------|------------------|
| 7B          | 4.5GB            |
| 7B-q2_K     | 5.37GB           |
| 7B-q3_K_L   | 6.10GB           |
| 7B-q4_1     | 6.71GB           |
| 7B-q4_K_M   | 6.58GB           |
| 7B-q5_1     | 7.56GB           |
| 7B-q5_K_M   | 7.28GB           |
| 7B-q6_K     | 8.03GB           |
| 7B-q8_0     | 9.66GB           |
| 13B         | 12GB             |
| 13B-q2_K    | 8.01GB           |
| 13B-q3_K_L  | 9.43GB           |
| 13B-q4_1    | 10.64GB          |
| 13B-q4_K_M  | 10.37GB          |
| 13B-q5_1    | 12.26GB          |
| 13B-q5_K_M  | 11.73GB          |
| 13B-q6_K    | 13.18GB          |
| 13B-q8_0    | 16.33GB          |
| 33B         | 20GB             |
| 33B-q2_K    | 16.21GB          |
| 33B-q3_K_L  | 19.78GB          |
| 33B-q4_1    | 22.83GB          |
| 33B-q4_K_M  | 22.12GB          |
| 33B-q5_1    | 26.90GB          |
| 33B-q5_K_M  | 25.55GB          |
| 33B-q6_K    | 29.19GB          |
| 33B-q8_0    | 37.06GB          |
| 65B         | 50GB             |
| 65B-q2_K    | 29.95GB          |
| 65B-q3_K_L  | 37.15GB          |
| 65B-q4_1    | 43.31GB          |
| 65B-q4_K_M  | 41.85GB          |
| 65B-q5_1    | 51.47GB          |
| 65B-q5_K_M  | 48.74GB          |
| 65B-q6_K    | 56.06GB          |
| 65B-q8_0    | 71.87GB          |

## 💬 Support

Need help? Join our [Discord](https://discord.gg/62Hc6FEYQH)

## 🤝 Contributing

If you discover a bug or have a feature idea, feel free to open an issue or PR.

To run Serge in development mode:

```bash
git clone https://github.com/serge-chat/serge.git
docker compose -f docker-compose.dev.yml up -d --build
```
