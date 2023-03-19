# Serge

A very simple dockerized setup to answer chat-like questions using `llama.cpp` and alpaca models.

## Getting started

```
git clone git@github.com:nsarrazin/alpaca-api.git
```

Put your weights in the `models` folder. You can download them using the following magnet links:

- [ggml-alpaca-7b-q4.bin](https://maglit.me/corotlesque)
- [ggml-alpaca-13b-q4.bin](https://maglit.me/nonchoodithvness)

Afterwards navigate to the `alpaca-api` folder and run:

```
cp .env.sample .env
docker compose up -d
```

Then navigate to http://localhost:9123/docs to get the API definition.

## What's next

- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.
- [ ] Stop words support

And a lot more!
