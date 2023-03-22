# Serge - LLaMa made easy 🦙

![License](https://img.shields.io/github/license/nsarrazin/serge)

A chat interface based on `llama.cpp` for running Alpaca models. Entirely self-hosted, no API keys needed. Fits on 4GB of RAM and runs on the CPU.

- **SvelteKit** frontend
- **MongoDB** for storing chat history & parameters
- **FastAPI + beanie** for the API, wrapping calls to `llama.cpp`

[demo.webm](https://user-images.githubusercontent.com/25119303/226897188-914a6662-8c26-472c-96bd-f51fc020abf6.webm)

## Getting started

Setting up Serge is very easy. TLDR for running it with Alpaca 7B:

```
git clone git@github.com:nsarrazin/serge.git
cd serge

cp .env.sample .env

docker compose up -d
docker compose exec api python3 /usr/src/app/utils/download.py tokenizer 7B 13B
```

(You will need `huggingface_hub` for fetching the tokenizer, just run `pip install huggingface_hub` before if you don't have it, no setup needed. Otherwise just [download the file manually](https://huggingface.co/decapoda-research/llama-7b-hf/blob/main/tokenizer.model))

Then just go to http://localhost:8008/ and you're good to go!

## Getting the weights

You will need to download the weights for the model you want to use. Currently we only support 7B and 13B models. Place the downloaded weights in the `api/weights` folder.

### 7B (~4GB of ram)

Recommmended way is from huggingface. One-liner:

```
python -c 'from huggingface_hub import hf_hub_download; hf_hub_download(repo_id="Pi3141/alpaca-7B-ggml", filename="ggml-model-q4_0.bin", local_dir=".", local_dir_use_symlinks=False)'
mv ggml-model-q4_0.bin api/weights/ggml-alpaca-7b-q4.bin
```

Or you can download the file manually from [here](https://huggingface.co/Pi3141/alpaca-7B-ggml/resolve/main/ggml-model-q4_0.bin) and place it in the `api/weights` folder.

Alternatives :

```
# torrent
magnet:?xt=urn:btih:053b3d54d2e77ff020ebddf51dad681f2a651071&dn=ggml-alpaca-13b-q4.bin&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fopentracker.i2p.rocks%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.com%3a2810%2fannounce

# or any of these should work
curl -o ggml-alpaca-7b-q4.bin -C - https://gateway.estuary.tech/gw/ipfs/QmQ1bf2BTnYxq73MFJWu1B7bQ2UD6qG7D7YDCxhTndVkPC
curl -o ggml-alpaca-7b-q4.bin -C - https://ipfs.io/ipfs/QmQ1bf2BTnYxq73MFJWu1B7bQ2UD6qG7D7YDCxhTndVkPC
curl -o ggml-alpaca-7b-q4.bin -C - https://cloudflare-ipfs.com/ipfs/QmQ1bf2BTnYxq73MFJWu1B7bQ2UD6qG7D7YDCxhTndVkPC
```

### 13B (~10GB of ram)

Recommmended way is from huggingface. One-liner:

```
python -c 'from huggingface_hub import hf_hub_download; hf_hub_download(repo_id="Pi3141/alpaca-13B-ggml", filename="ggml-model-q4_0.bin", local_dir=".", local_dir_use_symlinks=False)'
mv ggml-model-q4_0.bin api/weights/ggml-alpaca-13b-q4.bin
```

Or you can download the file manually from [here](https://huggingface.co/Pi3141/alpaca-13B-ggml/resolve/main/ggml-model-q4_0.bin) and place it in the `api/weights` folder.

Alternatives:

```
# torrent
magnet:?xt=urn:btih:053b3d54d2e77ff020ebddf51dad681f2a651071&dn=ggml-alpaca-13b-q4.bin&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fopentracker.i2p.rocks%3a6969%2fannounce&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.com%3a2810%2fannounce

# or any of these should work
curl -o ggml-alpaca-13b-q4.bin -C - https://gateway.estuary.tech/gw/ipfs/Qme6wyw9MzqbrUMpFNVq42rC1kSdko7MGT9CL7o1u9Cv9G
curl -o ggml-alpaca-13b-q4.bin -C - https://ipfs.io/ipfs/Qme6wyw9MzqbrUMpFNVq42rC1kSdko7MGT9CL7o1u9Cv9G
curl -o ggml-alpaca-13b-q4.bin -C - https://cloudflare-ipfs.com/ipfs/Qme6wyw9MzqbrUMpFNVq42rC1kSdko7MGT9CL7o1u9Cv9G
```

### 30B ~(30GB of ram)

Recommmended way is from huggingface. One-liner:

```
python -c 'from huggingface_hub import hf_hub_download; hf_hub_download(repo_id="Pi3141/alpaca-30B-ggml", filename="ggml-model-q4_0.bin", local_dir=".", local_dir_use_symlinks=False)'
mv ggml-model-q4_0.bin api/weights/ggml-alpaca-30b-q4.bin
```

Or you can download the file manually from [here](https://huggingface.co/Pi3141/alpaca-30B-ggml/resolve/main/ggml-model-q4_0.bin) and place it in the `api/weights` folder. No alternatives yet.

### Model conversion

Note: `llama.cpp` [recently underwent some change](https://github.com/ggerganov/llama.cpp/issues/324#issuecomment-1476227818) that requires model weights to be converted to a new format. Serge picks this up automatically on startup, and will convert your weights to the new format if needed. The old weights will be renamed to `*.bin.old` and the new weights will be named `*.bin`.

## What's next

- [x] Front-end to interface with the API
- [x] Pass model parameters when creating a chat
- [ ] User profiles & authentication
- [ ] Different prompt options
- [ ] LangChain integration with a custom LLM
- [ ] Support for other llama models, quantization, etc.

And a lot more!
