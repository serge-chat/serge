# alpaca-api

A very simple dockerized API for interacting with alpaca through llama.cpp (currently doesn't support other LLaMA models)

## Getting started

```
git clone git@github.com:nsarrazin/alpaca-api.git
```

Put your weights in the `models` folder. You can download them using the following magnet links:

- [`ggml-alpaca-7b-q4.bin`](magnet:?xt=urn:btih:5aaceaec63b03e51a98f04fd5c42320b2a033010&dn=ggml-alpaca-7b-q4.bin&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fopentracker.i2p.rocks%3a6969%2fannounce)
- [`ggml-alpaca-13b-q4.bin`](magnet:?xt=urn:btih:053b3d54d2e77ff020ebddf51dad681f2a651071&dn=ggml-alpaca-13b-q4.bin&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fopentracker.i2p.rocks%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.com%3a2810%2fannounce)

Afterwards navigate to the `alpaca-api` folder and run:

```
docker compose build
docker compose up -d
```

Then navigate to http://localhost:9123/docs to get the API definition.

## What's next

- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.
- [ ] Stop words support

And a lot more!
