<script lang="ts">
  import "../app.css";
  import type { LayoutData } from "./$types";
  import { invalidate, goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  export let data: LayoutData;

  let deleteConfirm = false;
  let theme: string;
  let bar_visible: boolean;
  
  onMount(() => {
    bar_visible = window.innerWidth > 768;
    theme = localStorage.getItem("data-theme") || "light";
    document.documentElement.setAttribute("data-theme", theme);
  });

  $: id = $page.params.id || "";
  async function deleteChat(chatID: string) {
    const response = await fetch("/api/chat/" + chatID, { method: "DELETE" });
    if (response.status === 200) {
      toggleDeleteConfirm();
      await goto("/");
      await invalidate("/api/chat/");
    } else {
      console.error("Error " + response.status + ": " + response.statusText);
    }
  }

  function toggleDeleteConfirm() {
    deleteConfirm = !deleteConfirm;
  }

  function timeSince(datestring: string) {
    const date = new Date(datestring);
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

    let interval = seconds / 31536000;

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

  function toggleTheme() {
    theme = theme === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("data-theme", theme);
  }

  function toggleBar() {
    bar_visible = !bar_visible;
  }
</script>

<aside
  id="default-sidebar"
  class={"fixed left-0 top-0 z-40 h-screen w-80 -translate-x-full border-r border-base-content/[.2] transition-transform" + (bar_visible ? " translate-x-0" : "")}
  aria-label="Sidebar"
>

  <div class="relative h-full overflow-y-auto bg-base-200 px-3 py-4">
    <ul class="space-y-2">
      <li class="pt-4">
        <div class="flex justify-center items-center">
        <a href="/" class="btn-outline btn h-6 w-48 font-semibold mr-4"> Home </a>
        <button class="btn btn-outline h-6 w-16 font-semibold justify-center items-center flex" on:click={toggleBar}>
          <svg
            viewBox="0 0 100 73"
            width="30"
            height="30"
            xmlns="http://www.w3.org/2000/svg"
            >
            <rect x="10" y="14" width="80" height="3" rx="10" fill= { (theme == "dark")? "white" : "black" }></rect>
            <rect x="10" y="43" width="80" height="3" rx="10" fill= { (theme == "dark")? "white" : "black" }></rect>
            <rect x="10" y="72" width="80" height="3" rx="10" fill= { (theme == "dark")? "white" : "black" }></rect>
          </svg>
         </button>
        </div>
      </li>
      {#each data.chats as chat}
        <li>
          <a
            href={"/chat/" + chat.id}
            class="flex items-center rounded-lg p-2 text-base font-normal hover:bg-gradient-to-r hover:from-base-100 hover:to-transparent hover:text-base-content"
            class:bg-base-300={id === chat.id}
          >
            <div class="flex w-full flex-col">
              <div class="flex w-full flex-col items-start justify-start">
                <div class="flex w-full flex-row items-center justify-between">
                  <p class="text-sm font-light">
                    {truncate(chat.subtitle, 28)}
                  </p>
                  {#if $page.params.id === chat.id}
                    {#if deleteConfirm}
                      <div class="flex flex-row items-center">
                        <button
                          name="confirm-delete"
                          class="btn-ghost btn-sm btn"
                          on:click|preventDefault={() => deleteChat(chat.id)}
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 16 16"
                            width="16"
                            height="16"
                          >
                            <path
                              class="fill-base-content"
                              d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm1.5 0a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Zm10.28-1.72-4.5 4.5a.75.75 0 0 1-1.06 0l-2-2a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018l1.47 1.47 3.97-3.97a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042Z"
                            />
                          </svg>
                        </button>
                        <button
                          name="cancel-delete"
                          class="btn-ghost btn-sm btn"
                          on:click|preventDefault={toggleDeleteConfirm}
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 16 16"
                            width="16"
                            height="16"
                          >
                            <path
                              class="fill-base-content"
                              d="M2.344 2.343h-.001a8 8 0 0 1 11.314 11.314A8.002 8.002 0 0 1 .234 10.089a8 8 0 0 1 2.11-7.746Zm1.06 10.253a6.5 6.5 0 1 0 9.108-9.275 6.5 6.5 0 0 0-9.108 9.275ZM6.03 4.97 8 6.94l1.97-1.97a.749.749 0 0 1 1.275.326.749.749 0 0 1-.215.734L9.06 8l1.97 1.97a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215L8 9.06l-1.97 1.97a.749.749 0 0 1-1.275-.326.749.749 0 0 1 .215-.734L6.94 8 4.97 6.03a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018Z"
                            />
                          </svg>
                        </button>
                      </div>
                    {:else}
                      <button
                        class="btn-ghost btn-sm btn"
                        on:click|preventDefault={toggleDeleteConfirm}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 16 16"
                          width="16"
                          height="16"
                        >
                          <path
                            class="fill-base-content"
                            d="M11 1.75V3h2.25a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1 0-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75ZM4.496 6.675l.66 6.6a.25.25 0 0 0 .249.225h5.19a.25.25 0 0 0 .249-.225l.66-6.6a.75.75 0 0 1 1.492.149l-.66 6.6A1.748 1.748 0 0 1 10.595 15h-5.19a1.75 1.75 0 0 1-1.741-1.575l-.66-6.6a.75.75 0 1 1 1.492-.15ZM6.5 1.75V3h3V1.75a.25.25 0 0 0-.25-.25h-2.5a.25.25 0 0 0-.25.25Z"
                          />
                        </svg>
                      </button>
                    {/if}
                  {/if}
                </div>
                <span class="text-xs font-semibold">{chat.model}</span>
                <span class="text-xs">{timeSince(chat.created) + " ago"}</span>
              </div>
            </div>
          </a>
        </li>
      {/each}
    </ul>
    <div class="absolute top-[92%] bottom-0 left-0 right-0 m-5">
      <div class="inline-flex justify-center w-full">
        🌞
        <input
          on:click={toggleTheme}
          type="checkbox"
          class="toggle inline-block w-12 mx-1"
          checked
        />
        🌚
      </div>
    </div>
  </div>
</aside>

{#if !bar_visible}
<button class="fixed btn btn-outline h-6 w-16 font-semibold justify-center items-center flex m-2" on:click={toggleBar}>
  <svg
  viewBox="0 0 100 73"
  width="30"
  height="30"
  xmlns="http://www.w3.org/2000/svg"
>
  <rect x="10" y="14" width="80" height="3" rx="10" fill= { (theme == "dark")? "white" : "black" }></rect>
  <rect x="10" y="43" width="80" height="3" rx="10" fill= { (theme == "dark")? "white" : "black" }></rect>
  <rect x="10" y="72" width="80" height="3" rx="10" fill= { (theme == "dark")? "white" : "black" }></rect>
</svg>
 </button>
{/if}

<div class={"h-full transition-all" + ((bar_visible) ? " md:ml-80" : "")}>
  <slot />
</div>
