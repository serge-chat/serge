<script lang="ts">
  import "../app.css";
  import type { LayoutData } from "./$types";

  export let data: LayoutData;
</script>

<aside
  id="default-sidebar"
  class="fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0"
  aria-label="Sidebar"
>
  <div class="h-full px-3 py-4 overflow-y-auto bg-gray-50 dark:bg-gray-800">
    <ul class="space-y-2 h-full">
      {#each data.chats as chat}
        <li>
          <a
            href={"/chat/" + chat}
            class="flex items-center p-2 text-base font-normal text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <span class="ml-3">{chat}</span>
          </a>
        </li>
      {/each}
      <li class="mt-auto">
        <a
          href={"/"}
          class="flex items-center p-2 text-base font-normal text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <span class="ml-3">Home</span>
        </a>
      </li>
    </ul>
  </div>
</aside>

<div class="p-4 sm:ml-64">
  <slot />
</div>

<style lang="postcss">
  :global(html) {
    background-color: theme(colors.gray.100);
  }
</style>
