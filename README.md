# Serge - LLaMA made easy 🦙

![License](https://img.shields.io/github/license/serge-chat/serge)
[![Discord](https://img.shields.io/discord/1088427963801948201?label=Discord)](https://discord.gg/62Hc6FEYQH)

Serge is a chat interface crafted with [llama.cpp](https://github.com/ggerganov/llama.cpp) for running GGUF models. No API keys, entirely self-hosted!

- 🌐 **SvelteKit** frontend
- 💾 **[Redis](https://github.com/redis/redis)** for storing chat history & parameters
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

## 🖥️ Windows

Ensure you have Docker Desktop installed, WSL2 configured, and enough free RAM to run models. 

## ☁️ Kubernetes

Instructions for setting up Serge on Kubernetes can be found in the [wiki](https://github.com/serge-chat/serge/wiki/Integrating-Serge-in-your-orchestration#kubernetes-example).

## 🧠 Supported Models

| Category      | Models |
|:-------------:|:-------|
| **CodeLLaMA** | 7B, 13B |
| **Falcon** | 7B, 7B-Instruct, 40B, 40B-Instruct |
| **LLaMA**  | 7B, 13B, 70B |
| **Meditron** | 7B, 70B |
| **Mistral** | 7B, 7B-Instruct, 7B-OpenOrca |
| **Neural-Chat ** | 7B-v3.1 | 
| **OpenLLaMA** | 3B-v2, 7B-v2, 13B-v2 |
| **Orca-2** | 7B, 13B |
| **Vicuna** | 7B-v1.5, 13B-v1.5 |
| **Zephyr** | 7B-Alpha, 7B-Beta |

Additional weights can be added to the `serge_weights` volume using `docker cp`:

```bash
docker cp ./my_weight.bin serge:/usr/src/app/weights/
```

## ⚠️ Memory Usage

LLaMA will crash if you don't have enough available memory for the model:

## 💬 Support

Need help? Join our [Discord](https://discord.gg/62Hc6FEYQH)

## ⭐️ Stargazers

<img src="https://starchart.cc/serge-chat/serge.svg" alt="Stargazers over time" style="max-width: 100%">

## 🧾 License

[Nathan Sarrazin](https://github.com/nsarrazin) and [Contributors](https://github.com/serge-chat/serge/graphs/contributors). `Serge` is free and open-source software licensed under the [MIT License](https://github.com/serge-chat/serge/blob/main/LICENSE-MIT) and [Apache-2.0](https://github.com/serge-chat/serge/blob/main/LICENSE-APACHE).

## 🤝 Contributing

If you discover a bug or have a feature idea, feel free to open an issue or PR.

To run Serge in development mode:
```bash
git clone https://github.com/serge-chat/serge.git
docker compose -f docker-compose.dev.yml up -d --build
```
