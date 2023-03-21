# Serge - LLaMa made easy 🦙

![License](https://img.shields.io/github/license/nsarrazin/serge)

|              Home page               |                       Chat                       |
| :----------------------------------: | :----------------------------------------------: |
| ![](https://i.imgur.com/CRXj9KD.png) | ![Serge - chat](https://i.imgur.com/bnqZyaC.png) |

A chat interface based on `llama.cpp` for running alpaca models.

- **SvelteKit** frontend
- **MongoDB** for storing chat history & parameters
- **FastAPI + beanie** for the API, wrapping calls to `llama.cpp`

## Getting started

Setting up Serge is very easy. Start by cloning the repo:

```
git clone git@github.com:nsarrazin/serge.git
```

Then put your weights in the `models` folder. If you don't have them you can download them using the following magnet links:

- [ggml-alpaca-7b-q4.bin](https://maglit.me/corotlesque)
- [ggml-alpaca-13b-q4.bin](https://maglit.me/nonchoodithvness)

They are currently the only two models supported. I'm working on expanding support to all the models supported by `llama.cpp`.

Note: `llama.cpp` [recently underwent some change](https://github.com/ggerganov/llama.cpp/issues/324#issuecomment-1476227818) that requires model weights to be converted to a new format. Serge picks this up automatically on startup, and will convert your weights to the new format if needed. The old weights will be renamed to `*.bin.old` and the new weights will be named `*.bin`.

Then, you can start the project by running:

```
cp .env.sample .env
docker compose up -d
```

The front-end lives at http://localhost:8008/ by default but you can change the port in the `.env` file.

The interactive API docs is available at http://localhost:8008/api/docs.

## What's next

- [x] Front-end to interface with the API
- [x] Pass model parameters when creating a chat
- [ ] User profiles & authentication
- [ ] Different prompt options
- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.

And a lot more!
