<script lang="ts">
  import { invalidate } from "$app/navigation";
  import type { PageData } from "./$types";
  import RefreshModal from "../../lib/components/models/RefreshModal.svelte";

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

<div class="flex flex-row items-center justify-center pt-5">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    width="24"
    height="24"
    ><path
      class="fill-warning"
      d="M9.504.43a1.516 1.516 0 0 1 2.437 1.713L10.415 5.5h2.123c1.57 0 2.346 1.909 1.22 3.004l-7.34 7.142a1.249 1.249 0 0 1-.871.354h-.302a1.25 1.25 0 0 1-1.157-1.723L5.633 10.5H3.462c-1.57 0-2.346-1.909-1.22-3.004L9.503.429Zm1.047 1.074L3.286 8.571A.25.25 0 0 0 3.462 9H6.75a.75.75 0 0 1 .694 1.034l-1.713 4.188 6.982-6.793A.25.25 0 0 0 12.538 7H9.25a.75.75 0 0 1-.683-1.06l2.008-4.418.003-.006a.036.036 0 0 0-.004-.009l-.006-.006-.008-.001c-.003 0-.006.002-.009.004Z"
    /></svg
  >
  <h1 class="px-2 text-center text-3xl font-bold">Download a model</h1>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 16 16"
    width="24"
    height="24"
    ><path
      class="fill-warning"
      d="M9.504.43a1.516 1.516 0 0 1 2.437 1.713L10.415 5.5h2.123c1.57 0 2.346 1.909 1.22 3.004l-7.34 7.142a1.249 1.249 0 0 1-.871.354h-.302a1.25 1.25 0 0 1-1.157-1.723L5.633 10.5H3.462c-1.57 0-2.346-1.909-1.22-3.004L9.503.429Zm1.047 1.074L3.286 8.571A.25.25 0 0 0 3.462 9H6.75a.75.75 0 0 1 .694 1.034l-1.713 4.188 6.982-6.793A.25.25 0 0 0 12.538 7H9.25a.75.75 0 0 1-.683-1.06l2.008-4.418.003-.006a.036.036 0 0 0-.004-.009l-.006-.006-.008-.001c-.003 0-.006.002-.009.004Z"
    /></svg
  >
</div>

<h1 class="pb-5 pt-2 text-center text-xl font-light">
  Make sure you have enough disk space and available RAM to run them.<br />
  7B requires about 4.5GB of free RAM, 13B requires about 12GB free, 30B requires
  about 20GB free
</h1>

<div class="mx-auto w-fit">
  <RefreshModal />
</div>

<div class="mt-30 mx-auto flex flex-col">
  <div class="mx-auto w-full max-w-4xl">
    <div class="divider" />
    {#each data.models as model}
      <div class="my-5 flex flex-col content-around">
        <div
          class="mx-auto flex flex-row items-center justify-center text-3xl font-semibold"
        >
          <span class="mr-2">{model.name}</span>
          {#if model.available}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 16 16"
              width="24"
              height="24"
            >
              <path
                class="fill-info"
                d="m9.585.52.929.68c.153.112.331.186.518.215l1.138.175a2.678 2.678 0 0 1 2.24 2.24l.174 1.139c.029.187.103.365.215.518l.68.928a2.677 2.677 0 0 1 0 3.17l-.68.928a1.174 1.174 0 0 0-.215.518l-.175 1.138a2.678 2.678 0 0 1-2.241 2.241l-1.138.175a1.17 1.17 0 0 0-.518.215l-.928.68a2.677 2.677 0 0 1-3.17 0l-.928-.68a1.174 1.174 0 0 0-.518-.215L3.83 14.41a2.678 2.678 0 0 1-2.24-2.24l-.175-1.138a1.17 1.17 0 0 0-.215-.518l-.68-.928a2.677 2.677 0 0 1 0-3.17l.68-.928c.112-.153.186-.331.215-.518l.175-1.14a2.678 2.678 0 0 1 2.24-2.24l1.139-.175c.187-.029.365-.103.518-.215l.928-.68a2.677 2.677 0 0 1 3.17 0ZM7.303 1.728l-.927.68a2.67 2.67 0 0 1-1.18.489l-1.137.174a1.179 1.179 0 0 0-.987.987l-.174 1.136a2.677 2.677 0 0 1-.489 1.18l-.68.928a1.18 1.18 0 0 0 0 1.394l.68.927c.256.348.424.753.489 1.18l.174 1.137c.078.509.478.909.987.987l1.136.174a2.67 2.67 0 0 1 1.18.489l.928.68c.414.305.979.305 1.394 0l.927-.68a2.67 2.67 0 0 1 1.18-.489l1.137-.174a1.18 1.18 0 0 0 .987-.987l.174-1.136a2.67 2.67 0 0 1 .489-1.18l.68-.928a1.176 1.176 0 0 0 0-1.394l-.68-.927a2.686 2.686 0 0 1-.489-1.18l-.174-1.137a1.179 1.179 0 0 0-.987-.987l-1.136-.174a2.677 2.677 0 0 1-1.18-.489l-.928-.68a1.176 1.176 0 0 0-1.394 0ZM11.28 6.78l-3.75 3.75a.75.75 0 0 1-1.06 0L4.72 8.78a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L7 8.94l3.22-3.22a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042Z"
              />
            </svg>
          {/if}
        </div>
        <p class="mx-auto pb-2 text-xl font-light">
          ({model.size / 1e9}GB)
        </p>
        {#if model.progress}
          <div class="mx-auto my-5 w-56 justify-center">
            <p class="w-full text-center font-light">{model.progress}%</p>
            <progress
              class="progress-primary progress mx-auto h-5 w-56"
              value={model.progress}
              max="100"
            />
          </div>
        {/if}
        {#if model.available}
          <button
            on:click={() => deleteModel(model.name)}
            class="btn-warning btn-outline btn mx-auto">Delete</button
          >
        {:else}
          <button
            on:click={() => onClick(model.name)}
            class="btn-primary btn mx-auto"
            class:model.available={() => "btn-outline"}
            disabled={model.available ||
              !!(model.progress && model.progress > 0)}
          >
            Download
          </button>
        {/if}
      </div>
      <div class="divider" />
    {/each}
  </div>
</div>
