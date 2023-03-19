# Serge 🦙

![License](https://img.shields.io/github/license/nsarrazin/serge)

A chat interface based on `llama.cpp` and alpaca models. Available through an API created with FastAPI. Stores chats on a mongoDB backend.

## Getting started

Setting up Serge is very easy. Start by cloning the repo:

```
git clone git@github.com:nsarrazin/serge.git
```

Then put your weights in the `models` folder. If you don't have them you can download them using the following magnet links:

- [ggml-alpaca-7b-q4.bin](https://maglit.me/corotlesque)
- [ggml-alpaca-13b-q4.bin](https://maglit.me/nonchoodithvness)

They are currently the only two models supported. I'm working on expanding support to all the models supported by `llama.cpp`.

Then, you can start the project by running:

```
cp .env.sample .env
docker compose up -d
```

Then navigate to http://localhost:9124/docs to get an interactive API documentation.

The front-end lives on http://localhost:9123/. (Currently WIP)

## What's next

- [ ] Front-end to interface with the API
- [ ] Pass model parameters when creating a chat
- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.
      And a lot more!
