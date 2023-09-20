<script lang="ts">
  import type { PageData } from "./$types";
  import { goto, invalidate } from "$app/navigation";
  import { barVisible } from "$lib/stores";
  import { onDestroy } from "svelte";
  export let data: PageData;

  const models = data.models.filter((el) => el.available);

  const modelAvailable = models.length > 0;
  const modelsLabels = models.map((el) => el.name);
  let bar_visible: boolean;
  const unsubscribe = barVisible.subscribe((value) => (bar_visible = value));

  let temp = 0.1;
  let top_k = 50;
  let top_p = 0.95;

  let max_length = 2048;
  let repeat_last_n = 64;
  let repeat_penalty = 1.3;

  let init_prompt =
    "Below is an instruction that describes a task. Write a response that appropriately completes the request.";

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
  function toggleBar() {
    bar_visible = !bar_visible;
    barVisible.set(bar_visible);
  }
  onDestroy(unsubscribe);
</script>

{#if !bar_visible}
  <button
    class="absolute p-0 top-1 left-2 md:left-16 h-10 w-10 min-h-0 btn btn-ghost flex items-center justify-center font-semibold z-40"
    on:click={toggleBar}
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      class="w-4 h-4"
    >
      <path
        d="M11.28 9.53 8.81 12l2.47 2.47a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215l-3-3a.75.75 0 0 1 0-1.06l3-3a.749.749 0 0 1 1.275.326.749.749 0 0 1-.215.734Z"
      >
      </path>
      <path
        d="M3.75 2h16.5c.966 0 1.75.784 1.75 1.75v16.5A1.75 1.75 0 0 1 20.25 22H3.75A1.75 1.75 0 0 1 2 20.25V3.75C2 2.784 2.784 2 3.75 2ZM3.5 3.75v16.5c0 .138.112.25.25.25H15v-17H3.75a.25.25 0 0 0-.25.25Zm13 16.75h3.75a.25.25 0 0 0 .25-.25V3.75a.25.25 0 0 0-.25-.25H16.5Z"
      >
      </path>
    </svg>
  </button>
{/if}
<div class="flex flex-col items-center justify-center pt-5">
  <h1 class="pb-2 text-3xl font-bold">Say Hi to Serge</h1>
</div>
<h1 class="pb-5 pt-2 text-center text-xl font-light">
  An easy way to chat with Alpaca & other LLaMA based models.
</h1>

<form on:submit|preventDefault={onCreateChat} id="form-create-chat" class="p-5">
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

  <div tabindex="-1" class="collapse-arrow rounded-box collapse bg-base-200">
    <input type="checkbox" />
    <div class="collapse-title text-xl font-medium">Model settings</div>
    <div class="collapse-content">
      <div class="grid grid-cols-3 gap-4 p-3">
        <div
          class="tooltip tooltip-bottom col-span-2"
          data-tip="The higher the temperature, the more random the model output."
        >
          <label for="temperature" class="label-text"
            >Temperature - [{temp}]</label
          >
          <input
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
          data-tip="The number of samples to consider for top_k sampling."
        >
          <label for="top_k" class="label-text pb-1">top_k</label>
          <input
            class="input-bordered input w-full max-w-xs"
            name="top_k"
            type="number"
            bind:value={top_k}
            min="0"
            max="100"
          />
        </div>
        <div
          class="tooltip tooltip-bottom col-span-2"
          data-tip="Max text generated token"
        >
          <label for="max_length" class="label-text"
            >Maximum generated tokens - [{max_length}]</label
          >
          <input
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
          data-tip="The cumulative probability of the tokens to keep for nucleus sampling."
        >
          <label for="top_p" class="label-text pb-1">top_p</label>
          <input
            class="input-bordered input w-full max-w-xs"
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
          <label for="context_window" class="label-text"
            >Context Length - [{context_window}]</label
          >
          <input
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
          data-tip="Number of tokens to look back on for deciding to apply the repeat penalty."
        >
          <label for="repeat_last_n" class="label-text pb-1"
            >repeat_last_n</label
          >
          <input
            class="input-bordered input w-full max-w-xs"
            name="repeat_last_n"
            type="number"
            bind:value={repeat_last_n}
            min="0"
            max="100"
          />
        </div>
        <div class="flex flex-col">
          <label for="model" class="label-text pb-1"> Model choice</label>
          <select name="model" class="select-bordered select w-full max-w-xs">
            {#each modelsLabels as model}
              <option value={model}>{model}</option>
            {/each}
          </select>
        </div>
        <div
          class="tooltip flex flex-col"
          data-tip="The weight of the penalty to avoid repeating the last repeat_last_n tokens."
        >
          <label for="repeat_penalty" class="label-text pb-1">
            repeat_penalty
          </label>
          <input
            class="input-bordered input w-full max-w-xs"
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
            class="textarea-bordered textarea h-24 w-full"
            name="init_prompt"
            bind:value={init_prompt}
            placeholder="Enter your prompt here"
          />
        </div>
      </div>
    </div>
  </div>
</form>
