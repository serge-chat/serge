<script lang="ts">
  import type { PageData } from "./$types";

  export let data: PageData;
</script>

<h1 class="text-3xl font-bold text-center">Say Hi to Serge !</h1>

<form method="POST" class="p-10">
  <label for="model" class="label">
    <span class="label-text">Model</span>
  </label>
  <select name="model" class="select select-bordered w-full max-w-xs">
    {#each data.models as model}
      <option value={model}>{model}</option>
    {/each}
  </select>
  <button class="btn ml-5">Start a new chat</button>
</form>
