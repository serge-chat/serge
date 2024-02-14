<script lang="ts">
  import type { PageData } from "./$types";
  import { goto, invalidate } from "$app/navigation";
  export let data: PageData;

  const models = data.models.filter((el) => el.available);

  const modelAvailable = models.length > 0;
  const modelsLabels = models.map((el) => el.name);

  let temp = 0.1;
  let top_k = 50;
  let top_p = 0.95;

  let max_length = 2048;
  let repeat_last_n = 64;
  let repeat_penalty = 1.3;

  let init_prompt =
    "Below is an instruction that describes a task. Write a response that appropriately completes the request.";

  let n_threads = 4;
  let context_window = 2048;
  let gpu_layers = 0;

  async function onCreateChat(event: Event) {
    const form = document.getElementById("form-create-chat") as HTMLFormElement;

    const formData = new FormData(form);

    const convertedFormEntries = Array.from(formData, ([key, value]) => [
      key,
      typeof value === "string" ? value : value.name,
    ]);
    const searchParams = new URLSearchParams(convertedFormEntries);

    const r = await fetch("/api/chat/?" + searchParams.toString(), {
      method: "POST",
    });

    if (r.ok) {
      const data = await r.json();
      await goto("/chat/" + data);
      await invalidate("/api/chat/");
    }
  }
</script>

<div class="flex flex-col items-center justify-center pt-5">
  <h1 class="pb-2 text-3xl font-bold">Say Hi to Serge</h1>
</div>
<h1 class="pb-5 pt-2 text-center text-xl font-light">
  An easy way to chat with LLaMA based models.
</h1>

<form
  on:submit|preventDefault={onCreateChat}
  id="form-create-chat"
  class="p-5"
  aria-label="Model Settings"
>
  <div class="w-full pb-20">
    <div class="mx-auto w-fit pt-5 flex flex-col lg:flex-row justify-center">
      <button
        type="submit"
        class="btn-primary btn mb-2 lg:mr-10 lg:mb-0"
        disabled={!modelAvailable}>Start a new chat</button
      >
      <button
        on:click={() => goto("/models")}
        type="button"
        class="btn-outline btn">Download Models</button
      >
    </div>
  </div>
  <div class="flex justify-center">
    <div class="grid grid-cols-3 gap-4 p-3 bg-base-200" id="model_settings">
      <div class="col-span-3 text-xl font-medium">Model settings</div>
      <div
        class="tooltip tooltip-bottom col-span-2"
        data-tip="Controls how random the generated text is. Higher temperatures lead to more random and creative text, while lower temperatures lead to more predictable and conservative text."
      >
        <label for="temperature" class="label-text"
          >Temperature - [{temp}]</label
        >
        <input
          id="temperature"
          name="temperature"
          type="range"
          bind:value={temp}
          min="0.05"
          max="2"
          step="0.05"
          class="range range-sm mt-auto"
        />
      </div>
      <div
        class="tooltip tooltip-bottom flex flex-col"
        data-tip="Controls the number of tokens that are considered when generating the next token. Higher values of top_k lead to more predictable text, while lower values of top_k lead to more creative text."
      >
        <label for="top_k" class="label-text pb-1">top_k</label>
        <input
          id="top_k"
          class="input-bordered input w-full"
          name="top_k"
          type="number"
          bind:value={top_k}
          min="0"
          max="100"
        />
      </div>
      <div
        class="tooltip tooltip-bottom col-span-2"
        data-tip="The maximum number of tokens that the model will generate. This parameter can be used to control the length of the generated text."
      >
        <label for="max_length" class="label-text"
          >Maximum generated tokens - [{max_length}]</label
        >
        <input
          id="max_length"
          name="max_length"
          type="range"
          bind:value={max_length}
          min="32"
          max="32768"
          step="16"
          class="range range-sm mt-auto"
        />
      </div>
      <div
        class="tooltip flex flex-col"
        data-tip="Controls the diversity of the generated text. Higher values of top_p lead to more diverse text, while lower values of top_p lead to less diverse text."
      >
        <label for="top_p" class="label-text pb-1">top_p</label>
        <input
          class="input-bordered input w-full"
          id="top_p"
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
        data-tip="The number of previous tokens that are considered when generating the next token. A longer context length can help the model to generate more coherent and informative text."
      >
        <label for="context_window" class="label-text"
          >Context Length - [{context_window}]</label
        >
        <input
          id="context_window"
          name="context_window"
          type="range"
          bind:value={context_window}
          min="16"
          max="2048"
          step="16"
          class="range range-sm mt-auto"
        />
      </div>
      <div
        class="tooltip col-span-2"
        data-tip="Number of layers to put on the GPU. The rest will be on the CPU."
      >
        <label for="gpu_layers" class="label-text"
          >GPU Layers - [{gpu_layers}]</label
        >
        <input
          id="gpu_layers"
          name="gpu_layers"
          type="range"
          bind:value={gpu_layers}
          min="0"
          max="100"
          step="1"
          class="range range-sm mt-auto"
        />
      </div>
      <div
        class="tooltip flex flex-col"
        data-tip="Defines the penalty associated with repeating the last 'n' tokens in a generated text sequence."
      >
        <label for="repeat_last_n" class="label-text pb-1">repeat_last_n</label>
        <input
          id="repeat_last_n"
          class="input-bordered input w-full"
          name="repeat_last_n"
          type="number"
          bind:value={repeat_last_n}
          min="0"
          max="100"
        />
      </div>
      <div class="flex flex-col">
        <label for="model" class="label-text pb-1"> Model choice</label>
        <select
          name="model"
          id="models"
          class="select-bordered select w-full"
          aria-haspopup="menu"
        >
          {#each modelsLabels as model}
            <option id={model} value={model}>{model}</option>
          {/each}
        </select>
      </div>
      <div
        class="tooltip flex flex-col"
        data-tip="Number of threads to run LLaMA on."
      >
        <label for="n_threads" class="label-text pb-1">n_threads</label>
        <input
          id="n_threads"
          class="input-bordered input w-full"
          name="n_threads"
          type="number"
          bind:value={n_threads}
          min="0"
          max="64"
        />
      </div>
      <div
        class="tooltip flex flex-col"
        data-tip="Defines the penalty assigned to the model when it repeats certain tokens or patterns in the generated text."
      >
        <label for="repeat_penalty" class="label-text pb-1">
          repeat_penalty
        </label>
        <input
          id="repeat_penalty"
          class="input-bordered input w-full"
          name="repeat_penalty"
          type="number"
          bind:value={repeat_penalty}
          min="0"
          max="2"
          step="0.05"
        />
      </div>
      <div class="col-span-3 flex flex-col">
        <label for="init_prompt" class="label-text pb-1">Prompt Template</label>
        <textarea
          class="textarea-bordered textarea h-24 w-full"
          name="init_prompt"
          bind:value={init_prompt}
          placeholder="Enter your prompt here"
        />
      </div>
    </div>
  </div>
</form>
