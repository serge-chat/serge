# Serge - LLaMA made easy 🦙

![License](https://img.shields.io/github/license/serge-chat/serge)
[![Discord](https://img.shields.io/discord/1088427963801948201?label=Discord)](https://discord.gg/62Hc6FEYQH)

Serge is a chat interface crafted with [llama.cpp](https://github.com/ggerganov/llama.cpp) for running LLM models. No API keys, entirely self-hosted!

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

Then, just visit http://localhost:8008, You can find the API documentation at http://localhost:8008/api/docs

### 🌍 Environment Variables

The following Environment Variables are available:

| Variable Name         | Description                                             | Default Value                        |
|-----------------------|---------------------------------------------------------|--------------------------------------|
| `SERGE_DATABASE_URL`  | Database connection string                              | `sqlite:////data/db/sql_app.db`      |
| `SERGE_JWT_SECRET`    | Key for auth token encryption. Use a random string      | `uF7FGN5uzfGdFiPzR`                  |
| `SERGE_SESSION_EXPIRY`| Duration in minutes before a user must reauthenticate   | `60`                                 |
| `NODE_ENV`            | Node.js running environment                             | `production`                         |

## 🖥️ Windows

Ensure you have Docker Desktop installed, WSL2 configured, and enough free RAM to run models.

## ⚠️ Memory Usage

LLaMA will crash if you don't have enough available memory for the model

## 💬 Support

Need help? Join our [Discord](https://discord.gg/62Hc6FEYQH)

## 🧾 License

[Nathan Sarrazin](https://github.com/nsarrazin) and [Contributors](https://github.com/serge-chat/serge/graphs/contributors). `Serge` is free and open-source software licensed under the [MIT License](https://github.com/serge-chat/serge/blob/main/LICENSE-MIT) and [Apache-2.0](https://github.com/serge-chat/serge/blob/main/LICENSE-APACHE).

## 🤝 Contributing

If you discover a bug or have a feature idea, feel free to open an issue or PR.

To run Serge in development mode:

```bash
git clone https://github.com/serge-chat/serge.git
cd serge/
docker compose -f docker-compose.dev.yml up --build
```

The solution will accept a python debugger session on port 5678. Example launch.json for VSCode:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Remote Debug",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/api",
                    "remoteRoot": "/usr/src/app/api/"
                }
            ],
            "justMyCode": false
        }
    ]
}
```
