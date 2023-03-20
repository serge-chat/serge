<script lang="ts">
  import "../app.css";
  import type { LayoutData } from "./$types";

  import Icon from "@iconify/svelte";

  export let data: LayoutData;

  function timeSince(datestring: string) {
    const date = new Date(datestring);
    var seconds = Math.floor((Date.now() - date.getTime()) / 1000);

    var interval = seconds / 31536000;

    if (interval > 1) {
      return Math.floor(interval) + " years";
    }
    interval = seconds / 2592000;
    if (interval > 1) {
      return Math.floor(interval) + " months";
    }
    interval = seconds / 86400;
    if (interval > 1) {
      return Math.floor(interval) + " days";
    }
    interval = seconds / 3600;
    if (interval > 1) {
      return Math.floor(interval) + " hours";
    }
    interval = seconds / 60;
    if (interval > 1) {
      return Math.floor(interval) + " minutes";
    }
    return Math.floor(seconds) + " seconds";
  }
</script>

<aside
  id="default-sidebar"
  class="fixed top-0 left-0 z-40 w-96 h-screen transition-transform -translate-x-full sm:translate-x-0"
  aria-label="Sidebar"
>
  <div class="h-full px-3 py-4 overflow-y-auto bg-gray-600">
    <ul class="space-y-2">
      <li class="pt-4">
        <a href="/" class="btn btn-outline h-6 w-full font-semibold"> Home </a>
      </li>
      {#each data.chats as chat}
        <li>
          <a
            href={"/chat/" + chat.id}
            class="flex items-center p-2 text-base font-normal rounded-lg hover:bg-gray-700"
          >
            <span class="font-semibold">{chat.model}</span>
            <span class="ml-3">{timeSince(chat.created) + " ago"}</span>
          </a>
        </li>
      {/each}
    </ul>
  </div>
</aside>

<div class="p-4 sm:ml-96">
  <slot />
</div>
