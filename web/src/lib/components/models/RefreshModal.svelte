<script lang="ts">
  import { invalidate, invalidateAll } from "$app/navigation";

  let dialogTag: HTMLDialogElement;
  let isLoading = false;

  let link =
    "https://raw.githubusercontent.com/serge-chat/serge/main/api/src/serge/data/models.json";

  const handleRefresh = async (e: Event) => {
    isLoading = true;
    const r = await fetch("/api/model/refresh", {
      method: "POST",
      body: new FormData(e.target as HTMLFormElement),
    });

    if (r.ok) {
      await invalidate("/api/model/all");
      dialogTag.close();
    } else {
      alert("Error refreshing models");
    }
    isLoading = false;
  };
</script>

<button class="btn-outline btn" on:click={() => dialogTag.showModal()}
  >Refresh Models</button
>
<dialog bind:this={dialogTag} class="modal">
  <form method="dialog" class="modal-box">
    <button class="btn-ghost btn-sm btn-circle btn absolute right-2 top-2"
      >✕</button
    >
    <form on:submit|preventDefault={handleRefresh}>
      <h3 class="text-lg font-bold">Model refresh</h3>
      <p class="py-4">
        Enter the URL of the JSON file containing the models below
      </p>
      <input
        type="text"
        name="url"
        class="input-bordered input-primary input mb-4 w-full"
        bind:value={link}
      />
      <div class="modal-action">
        <!-- if there is a button in form, it will close the modal -->
        <button type="submit" class="btn" disabled={isLoading}>
          {#if isLoading}
            <span class="loading loading-spinner" />
          {/if}
          Refresh
        </button>
      </div>
    </form>
  </form>
</dialog>
