# Serg

![License](https://img.shields.io/github/license/nsarrazin/serge)

A chat interface based on `llama.cpp` and alpaca models. Available through an API created with FastAPI. Stores chats on a mongoDB backend.

## Getting started

```
git clone git@github.com:nsarrazin/serge.git
```

Put your weights in the `models` folder. You can download them using the following magnet links:

- [ggml-alpaca-7b-q4.bin](https://maglit.me/corotlesque)
- [ggml-alpaca-13b-q4.bin](https://maglit.me/nonchoodithvness)

Afterwards navigate to the `serge` folder and run:

```
cp .env.sample .env
docker compose up -d
```

Then navigate to http://localhost:9123/docs to get the API definition.

## What's next

- [ ] Front-end to interface with the API
- [ ] Pass model parameters when creating a chat
- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.
      And a lot more!
