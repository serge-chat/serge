<script lang="ts">
  import type { PageData } from "./$types";

  export let data: PageData;

  const modelAvailable = data.models.length > 0;

  let temp = 0.1;
  let top_k = 50;
  let top_p = 0.95;

  let max_length = 256;
  let repeat_last_n = 64;
  let repeat_penalty = 1.3;

  let init_prompt =
    "Below is an instruction that describes a task. Write a response that appropriately completes the request. The response must be accurate, concise and evidence-based whenever possible. A complete answer is always ended by [end of text].";

  let n_threads = 4;
  let ctx_length = 512;
</script>

<h1 class="text-3xl font-bold text-center pt-5">Say Hi to Serge!</h1>
<h1 class="text-xl text-center pt-2 pb-5">
  An easy way to chat with Alpaca & other LLaMa based models.
</h1>

<form method="POST" class="p-5">
  <div class="w-full pb-20">
    <div class="mx-auto w-fit pt-5">
      <button class=" mx-auto btn btn-primary ml-5" disabled={!modelAvailable}
        >Start a new chat</button
      >
    </div>
  </div>

  <div
    tabindex="-1"
    class="collapse collapse-arrow border-2 rounded-box border-gray-600 bg-base-100"
  >
    <input type="checkbox" />
    <div class="collapse-title text-xl font-medium">Model settings</div>
    <div class="collapse-content">
      <div class="grid grid-cols-3 gap-4 p-3 ">
        <div
          class="tooltip col-span-2"
          data-tip="The higher the temperature, the more random the model output."
        >
          <label for="temp" class="label-text">Temperature - [{temp}]</label>
          <input
            name="temp"
            type="range"
            bind:value={temp}
            min="0.05"
            max="2"
            step="0.05"
            class="range range-sm mt-auto"
          />
        </div>
        <div
          class="flex flex-col tooltip"
          data-tip="The number of samples to consider for top_k sampling. "
        >
          <label for="top_k" class="label-text pb-1">top_k</label>
          <input
            class="input input-bordered w-full max-w-xs"
            name="top_k"
            type="number"
            bind:value={top_k}
            min="0"
            max="100"
          />
        </div>
        <div class="col-span-2">
          <label for="max_length" class="label-text"
            >Maximum generated text length in tokens - [{max_length}]</label
          >
          <input
            name="max_length"
            type="range"
            bind:value={max_length}
            min="16"
            max="512"
            step="16"
            class="range range-sm mt-auto"
          />
        </div>
        <div
          class="flex flex-col tooltip"
          data-tip="The cumulative probability of the tokens to keep for nucleus sampling. "
        >
          <label for="top_p" class="label-text pb-1">top_p</label>
          <input
            class="input input-bordered w-full max-w-xs"
            name="top_p"
            type="number"
            bind:value={top_p}
            min="0"
            max="1"
            step="0.025"
          />
        </div>
        <div
          class="tooltip col-span-2"
          data-tip="Size of the prompt context. Will determine how far the model will read back. Increases memory consumption."
        >
          <label for="ctx_length" class="label-text"
            >Prompt Context Length - [{ctx_length}]</label
          >
          <input
            name="ctx_length"
            type="range"
            bind:value={ctx_length}
            min="16"
            max="2048"
            step="16"
            class="range range-sm mt-auto"
          />
        </div>

        <div
          class="flex flex-col tooltip"
          data-tip="Number of tokens to look back on for deciding to apply the repeat penalty."
        >
          <label for="repeat_last_n" class="label-text pb-1"
            >repeat_last_n</label
          >
          <input
            class="input input-bordered w-full max-w-xs"
            name="repeat_last_n"
            type="number"
            bind:value={repeat_last_n}
            min="0"
            max="100"
          />
        </div>
        <div class="flex flex-col">
          <label for="model" class="label-text pb-1"> Model choice </label>
          <select name="model" class="select select-bordered w-full max-w-xs">
            {#each data.models as model}
              <option value={model}>{model}</option>
            {/each}
          </select>
        </div>
        <div
          class="flex flex-col tooltip"
          data-tip="Number of threads to run LLaMa on."
        >
          <label for="n_threads" class="label-text pb-1">n_threads</label>
          <input
            class="input input-bordered w-full max-w-xs"
            name="n_threads"
            type="number"
            bind:value={n_threads}
            min="0"
            max="64"
          />
        </div>
        <div
          class="flex flex-col tooltip"
          data-tip="The weight of the penalty to avoid repeating the last repeat_last_n tokens. "
        >
          <label for="repeat_penalty" class="label-text pb-1">
            repeat_penalty
          </label>
          <input
            class="input input-bordered w-full max-w-xs"
            name="repeat_penalty"
            type="number"
            bind:value={repeat_penalty}
            min="0"
            max="2"
            step="0.05"
          />
        </div>
        <div class="col-span-3 flex flex-col">
          <label for="init_prompt" class="label-text pb-1"
            >Pre-Prompt for initializing a conversation.</label
          >
          <textarea
            class="textarea h-24 textarea-bordered w-full"
            name="init_prompt"
            bind:value={init_prompt}
            placeholder="Enter your prompt here"
          />
        </div>
      </div>
    </div>
  </div>
</form>
