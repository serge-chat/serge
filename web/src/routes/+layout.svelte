<script lang="ts">
  import "../app.css";
  import type { LayoutData } from "./$types";
  import { onMount, afterUpdate } from 'svelte';
  export let data: LayoutData;

  $: deleteIcon = "&#128465;";
  $: deleteConfirm = false;
  $: currentChatID = "";

  onMount(refreshCurrent);
  afterUpdate(refreshCurrent);

  function refreshCurrent() {
    if(window.location.pathname.startsWith("/chat/")) {
      var urlPaths = window.location.pathname.split("/");
      currentChatID = urlPaths[urlPaths.length-1];
    }
    else {
      currentChatID = "";
    }
  }

  async function deleteChat(chatID) {
      var response = await fetch("/api/chat/" + chatID, { method: 'DELETE'});
      if(response.status == 200) {
        window.location = "/";
      }
      else {
        alert("Error " + response.status + ": " + response.statusText);
      }
  }

  function toggleDeleteConfirm() {
      deleteConfirm = !deleteConfirm;
      deleteIcon = deleteConfirm ? "&#9932;" : "&#128465;";
  }

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

  function truncate(str: string, n: number) {
    return str.length > n ? str.slice(0, n - 1) + "..." : str;
  }
</script>

<aside
  id="default-sidebar"
  class="fixed top-0 left-0 z-40 w-80 h-screen transition-transform -translate-x-full sm:translate-x-0"
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
            <div class="flex flex-col">
              <div>
                <span class="font-semibold">{chat.model}</span>
                <span class="ml-3">{timeSince(chat.created) + " ago"}</span>
                    {#if currentChatID == chat.id}
                        {#if deleteConfirm}
                            <button
                                class="btn btn-link btn-sm"
                                on:click|preventDefault={() => deleteChat(chat.id)} >
                                &#128504;
                            </button>
                        {/if}
                        <button
                            class="btn btn-link btn-sm"
                            on:click|preventDefault={toggleDeleteConfirm} >
                            {@html deleteIcon}
                        </button>
                    {/if}
              </div>
              <p class="font-light text-sm">{truncate(chat.subtitle, 100)}</p>
            </div>
          </a>
        </li>
      {/each}
    </ul>
  </div>
</aside>

<div class="p-4 sm:ml-80 h-full">
  <slot />
</div>
