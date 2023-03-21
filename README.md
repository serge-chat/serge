# Serge - LLaMa made easy 🦙

![License](https://img.shields.io/github/license/nsarrazin/serge)

A chat interface based on `llama.cpp` for running alpaca models.

- **SvelteKit** frontend
- **MongoDB** for storing chat history & parameters
- **FastAPI + beanie** for the API, wrapping calls to `llama.cpp`


https://user-images.githubusercontent.com/25119303/226756536-8c7fea67-3aba-4011-969a-742872fc2858.mp4



## Getting started

Setting up Serge is very easy. Start by cloning the repo.

```
git clone git@github.com:nsarrazin/serge.git
```

Now you need to get the weights.

### Getting the weights

You will need to download the weights for the model you want to use. Currently we only support 7B and 13B models.

#### 7B

For the 7B version use any of these links :

[ggml-alpaca-7b-q4.bin (magnet link)](https://maglit.me/corotlesque)

```
# or any of these should work
curl -o ggml-alpaca-7b-q4.bin -C - https://gateway.estuary.tech/gw/ipfs/QmQ1bf2BTnYxq73MFJWu1B7bQ2UD6qG7D7YDCxhTndVkPC
curl -o ggml-alpaca-7b-q4.bin -C - https://ipfs.io/ipfs/QmQ1bf2BTnYxq73MFJWu1B7bQ2UD6qG7D7YDCxhTndVkPC
curl -o ggml-alpaca-7b-q4.bin -C - https://cloudflare-ipfs.com/ipfs/QmQ1bf2BTnYxq73MFJWu1B7bQ2UD6qG7D7YDCxhTndVkPC
```

#### 13B

For the 13B version (10+GB RAM needed) you can use any of these links :

[ggml-alpaca-13b-q4.bin (magnet link)](https://maglit.me/nonchoodithvness)

```
# or any of these should work
curl -o ggml-alpaca-13b-q4.bin -C - https://gateway.estuary.tech/gw/ipfs/Qme6wyw9MzqbrUMpFNVq42rC1kSdko7MGT9CL7o1u9Cv9G
curl -o ggml-alpaca-13b-q4.bin -C - https://ipfs.io/ipfs/Qme6wyw9MzqbrUMpFNVq42rC1kSdko7MGT9CL7o1u9Cv9G
curl -o ggml-alpaca-13b-q4.bin -C - https://cloudflare-ipfs.com/ipfs/Qme6wyw9MzqbrUMpFNVq42rC1kSdko7MGT9CL7o1u9Cv9G
```

### Tokenizer

You will also need to put the `tokenizer.model` for LLaMa in the `api/weights` folder. [You can grab it here](https://huggingface.co/decapoda-research/llama-7b-hf/blob/main/tokenizer.model).

### Starting the project

Finally you can start the project by running:

```
cp .env.sample .env
docker compose up -d
```

The front-end lives at http://localhost:8008/ by default but you can change the port in the `.env` file.

The interactive API docs is available at http://localhost:8008/api/docs.

#### Model conversion

Note: `llama.cpp` [recently underwent some change](https://github.com/ggerganov/llama.cpp/issues/324#issuecomment-1476227818) that requires model weights to be converted to a new format. Serge picks this up automatically on startup, and will convert your weights to the new format if needed. The old weights will be renamed to `*.bin.old` and the new weights will be named `*.bin`.

## What's next

- [x] Front-end to interface with the API
- [x] Pass model parameters when creating a chat
- [ ] User profiles & authentication
- [ ] Different prompt options
- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.

And a lot more!
