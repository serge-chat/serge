<script lang="ts">
  import { invalidate } from "$app/navigation";
  import type { ModelStatus } from "../+page";
  import type { PageData } from "./$types";
  import Icon from "@iconify/svelte";

  // The main data object for the page
  export let data: PageData;

  let downloading = false;
  let searchQuery = "";
  let selectedVariant: Record<string, string> = {};

  setInterval(async () => {
    if (downloading) {
      await invalidate("/api/model/all");
    }
  }, 1000);

  /**
   * Debounce function to limit how often a function can be called.
   * @param func - The function to be debounced.
   * @param wait - The time to wait in milliseconds.
   * @returns A debounced version of the given function.
   */
  function debounce(func: (...args: any[]) => void, wait: number) {
    let timeout: ReturnType<typeof setTimeout>;
    return function (...args: any[]) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Update search query with debounce to improve performance
  const updateSearch = debounce((query: string) => {
    searchQuery = query;
  }, 300);

  /**
   * Wrapper function for fetch to include invalidate call on successful response.
   * @param url - The URL to fetch.
   * @param options - Fetch request options.
   * @returns The fetch response.
   */
  async function fetchWithInvalidate(url: string, options: any) {
    const response = await fetch(url, options);
    if (response.ok) {
      await invalidate("/api/model/all");
    }
    downloading = false;
    return response;
  }

  /**
   * Truncates a string to the specified length and appends an ellipsis.
   * @param str - The string to truncate.
   * @param maxLength - The maximum length of the truncated string.
   * @returns The truncated string with an ellipsis if needed.
   */
  function truncateString(str: string, maxLength: number): string {
    return str.length > maxLength
      ? str.substring(0, maxLength - 1) + "..."
      : str;
  }

  /**
   * Handles the action (download/delete) on a model.
   * @param model - The model name.
   * @param isAvailable - Boolean indicating if the model is available.
   */
  async function handleModelAction(model: string, isAvailable: boolean) {
    if (downloading) {
      return;
    }

    downloading = true;
    const url = `/api/model/${model}${isAvailable ? "" : "/download"}`;
    const method = isAvailable ? "DELETE" : "POST";
    await fetchWithInvalidate(url, { method });
  }

  /**
   * Groups models by their prefix.
   * @param models - Array of ModelStatus objects.
   * @returns An object grouping models by their prefix.
   */
  function groupModelsByPrefix(
    models: ModelStatus[],
  ): Record<string, ModelStatus[]> {
    return models.reduce(
      (acc, model) => {
        const prefix = model.name.split("-")[0];
        acc[prefix] = acc[prefix] || [];
        acc[prefix].push(model);
        return acc;
      },
      {} as Record<string, ModelStatus[]>,
    );
  }

  /**
   * Handles change in variant selection for a model.
   * @param modelPrefix - The prefix of the model.
   * @param event - The change event.
   */
  function handleVariantChange(modelPrefix: string, event: Event) {
    const target = event.target as HTMLSelectElement;
    selectedVariant[modelPrefix] = target.value;
  }

  /**
   * Retrieves model details based on the selected variant or default.
   * @param models - Array of ModelStatus objects.
   * @param prefix - The prefix of the model group.
   * @returns The selected or default ModelStatus object.
   */
  function getModelDetails(models: ModelStatus[], prefix: string): ModelStatus {
    return models.find((m) => m.name === selectedVariant[prefix]) || models[0];
  }

  // Reactive statements to filter and group models based on search query
  $: filteredModels = data.models
    .filter(
      (model) =>
        !downloadedOrDownloadingModels.includes(model) &&
        model.name.toLowerCase().includes(searchQuery.toLowerCase()),
    )
    .sort((a, b) => a.name.localeCompare(b.name));

  // Reactive statement with models grouped by prefix
  $: groupedModels = groupModelsByPrefix(filteredModels);

  // Reactive statement to filter models that are downloaded or downloading
  $: downloadedOrDownloadingModels = data.models
    .filter((model) => model.available || model.progress > 0)
    .sort((a, b) => a.name.localeCompare(b.name));
</script>

<div class="top-section">
  <div class="search-row">
    <input
      type="text"
      bind:value={searchQuery}
      class="input input-bordered flex-grow"
      placeholder="Search models..."
      on:input={(e) => {
        const target = e.target;
        if (target instanceof HTMLInputElement) {
          updateSearch(target.value);
        }
      }}
    />
  </div>
</div>

<div class="models-grid grid">
  {#each downloadedOrDownloadingModels as model}
    <div class="model card card-bordered">
      <div class="card-body">
        <h2 class="card-title">{truncateString(model.name, 24)}</h2>
        <div class="model-details">
          {#if model.progress}
            <div class="progress-bar">
              <progress value={model.progress} max="100"></progress> / {model.progress}%
            </div>
          {/if}
          {#if model.available}
            {#if model.available}
              <p>Size: {model.size / 1e9}GB</p>
            {/if}
            <button
              on:click={() =>
                model.available
                  ? handleModelAction(model.name, model.available)
                  : handleModelAction(model.name, model.available)}
              class="btn {model.available ? 'btn-error' : 'btn-warning'} mt-2"
            >
              <Icon icon="mdi:trash" width="32" height="32" />
            </button>
          {/if}
        </div>
      </div>
    </div>
  {/each}
</div>

<div class="models-grid grid">
  {#each Object.entries(groupedModels) as [prefix, models]}
    <div class="model-group card card-bordered">
      <div class="card-body">
        <h2 class="card-title">{truncateString(prefix, 24)}</h2>
        <div class="model-details">
          {#if models.length > 1}
            <select
              bind:value={selectedVariant[prefix]}
              on:change={(event) => handleVariantChange(prefix, event)}
            >
              {#each models as model}
                <option value={model.name}
                  >{truncateString(model.name, 32)}</option
                >
              {/each}
            </select>
          {/if}

          {#if models.length === 1 || selectedVariant[prefix]}
            {@const model = getModelDetails(models, prefix)}
            {#if models.length === 1}
              <h3>{truncateString(model.name, 24)}</h3>
            {/if}
            <p>Size: {model.size / 1e9}GB</p>
            {#if model.progress}
              <div class="mx-auto my-5 w-56 justify-center">
                <p class="w-full text-center font-light">
                  {model.progress}%
                </p>
                <progress
                  class="progress progress-primary mx-auto h-5 w-56"
                  value={model.progress}
                  max="100"
                />
              </div>
            {/if}
            <button
              on:click={() =>
                model.available
                  ? handleModelAction(model.name, model.available)
                  : handleModelAction(model.name, model.available)}
              class="btn {model.available ? 'btn-error' : 'btn-primary'} mt-2"
            >
              {#if model.available}
                <Icon icon="mdi:trash" width="32" height="32" />
              {:else}
                <Icon icon="ic:baseline-download" width="32" height="32" />
              {/if}
            </button>
          {/if}
        </div>
      </div>
    </div>
  {/each}
</div>
