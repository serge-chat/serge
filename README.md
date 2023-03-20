# Serge 🦙

![License](https://img.shields.io/github/license/nsarrazin/serge)

![Serge](https://i.imgur.com/JtWV72d.png)
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

The front-end lives at http://localhost:9123/.

To get an interactive API documentation go to http://localhost:9124/docs.

## What's next

- [x] Front-end to interface with the API
- [x] Pass model parameters when creating a chat
- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.
      And a lot more!
