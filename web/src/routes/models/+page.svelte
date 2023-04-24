<script lang="ts">
  import { invalidate } from "$app/navigation";
  import { each } from "svelte/internal";
  import type { PageData } from "./$types";

  export let data: PageData;

  let downloading = false;

  setInterval(async () => {
    if (downloading) {
      await invalidate("/api/model/all");
    }
  }, 2500);

  async function onClick(model: string) {
    if (downloading) {
      return;
    }

    downloading = true;
    const r = await fetch(`/api/model/${model}/download`, {
      method: "POST",
    });

    if (r.ok) {
      await invalidate("/api/model/all");
    }
    downloading = false;
  }

  async function deleteModel(model: string) {
    const r = await fetch(`/api/model/${model}`, {
      method: "DELETE",
    });

    if (r.ok) {
      await invalidate("/api/model/all");
    }
  }
</script>

<h1 class="text-3xl font-bold text-center pt-5">⚡ Download a model ⚡</h1>
<h1 class="text-xl font-light text-center pt-2 pb-5">
  Make sure you have enough disk space and available RAM to run them.
</h1>

<div class="flex flex-col mx-auto mt-30">
  <div class="max-w-4xl mx-auto w-full">
    <div class="divider" />
    {#each data.models as model}
      <div class="flex flex-col content-around my-5">
        <h2 class="text-3xl font-semibold mx-auto">
          {model.name}
          {#if model.available}
            <span class="text-xl">✔️</span>
          {/if}
        </h2>
        <p class="text-xl font-light mx-auto pb-2">
          ({model.size / 1e9}GB)
        </p>
        {#if model.progress}
          <div class="w-56 mx-auto my-5 justify-center">
            <p class="w-full text-center font-light">{model.progress}%</p>
            <progress
              class="progress progress-primary h-5 w-56 mx-auto"
              value={model.progress}
              max="100"
            />
          </div>
        {/if}
        {#if model.available}
          <button
            on:click={() => deleteModel(model.name)}
            class="btn btn-warning btn-outline mx-auto">Delete</button
          >
        {:else}
          <button
            on:click={() => onClick(model.name)}
            class="btn btn-primary mx-auto"
            class:model.available={() => "btn-outline"}
            disabled={model.available ||
              (model.progress && model.progress > 0 ? true : false)}
          >
            Download
          </button>
        {/if}
      </div>
      <div class="divider" />
    {/each}
  </div>
</div>
