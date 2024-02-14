<script lang="ts">
  import "../app.css";
  import type { PageData } from "./$types";
  import { invalidate, goto } from "$app/navigation";
  import { onMount, onDestroy } from "svelte";
  import { page } from "$app/stores";
  import { newChat, themeStore } from "$lib/stores.js";
  import { fly } from "svelte/transition";
  export let data: PageData;

  export let isSidebarOpen: boolean = true;

  let models;
  let modelAvailable: boolean;
  const isLoading = false;

  let deleteConfirm = false;
  let deleteAllConfirm = false;
  let theme: string;
  let dataCht: Response | any = null;
  const unsubscribe = newChat.subscribe((value) => (dataCht = value));

  function toggleSidebar(): void {
    isSidebarOpen = !isSidebarOpen;
  }

  function hideSidebar(): void {
    isSidebarOpen = false;
  }

  onMount(() => {
    theme = localStorage.getItem("data-theme") || "dark";
    document.documentElement.setAttribute("data-theme", theme);
  });

  $: if (data && data.models) {
    models = data.models.filter((el) => el.available);
    modelAvailable = models.length > 0;
  } else {
    models = [];
    modelAvailable = false;
  }

  $: id = $page.params.id || "";

  async function goToHome() {
    await goto("/");
  }

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

  async function deleteAllChat() {
    const response = await fetch("/api/chat/delete/all", { method: "DELETE" });
    if (response.status === 200) {
      toggleDeleteAllConfirm();
      await goto("/");
      await invalidate("/api/chat/");
    } else {
      console.error("Error " + response.status + ": " + response.statusText);
    }
  }

  function toggleDeleteConfirm() {
    deleteConfirm = !deleteConfirm;
  }

  function toggleDeleteAllConfirm() {
    deleteAllConfirm = !deleteAllConfirm;
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
    $themeStore = $themeStore === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", $themeStore);
    localStorage.setItem("data-theme", $themeStore);
  }

  onDestroy(() => {
    unsubscribe;
  });
</script>

<button
  on:click={toggleSidebar}
  class="border-base-content/[.2] btn btn-square z-10 my-1 mx-2 fixed border"
>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    class="inline-block w-5 h-5 stroke-current"
    ><path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M4 6h16M4 12h16M4 18h16"
    ></path></svg
  >
</button>

<aside
  class="border-base-content/[.2] fixed top-0 z-40 min-h-full border-r transition-all overflow-hidden aria-label=Sidebar"
  class:left-0={isSidebarOpen}
  class:-left-80={!isSidebarOpen}
>
  <div
    class="bg-base-200 relative h-screen py-1 px-2 overflow-hidden flex flex-col items-center justify-between"
  >
    <div class="w-full flex items-center pb-1">
      <button
        on:click={toggleSidebar}
        class="border-base-content/[.2] btn btn-square border"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          class="inline-block w-5 h-5 stroke-current"
          ><path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          ></path></svg
        >
      </button>
      <button
        disabled={isLoading || !modelAvailable}
        class="btn btn-ghost flex-grow h-6 font-semibold text-left text-sm capitalize"
        class:loading={isLoading}
        on:click|preventDefault={() => goto("/")}
        style="justify-content: flex-start;"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 16 16"
          fill="currentColor"
          class="w-4 h-4 mr-2"
        >
          <path
            d="M1 2.75C1 1.784 1.784 1 2.75 1h10.5c.966 0 1.75.784 1.75 1.75v7.5A1.75 1.75 0 0 1 13.25 12H9.06l-2.573 2.573A1.458 1.458 0 0 1 4 13.543V12H2.75A1.75 1.75 0 0 1 1 10.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h2a.75.75 0 0 1 .75.75v2.19l2.72-2.72a.749.749 0 0 1 .53-.22h4.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"
          >
          </path>
        </svg>
        <span>New Chat</span>
      </button>

      <button class="btn btn-ghost flex-shrink-0" on:click={goToHome}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="w-5 h-5"
        >
          <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
        </svg>
        <span class="sr-only">Home</span>
      </button>
    </div>
    <ul
      class="my-1 w-full flex-grow overflow-y-auto no-scrollbar firefox-no-scrollbar ie-edge-no-scrollbar"
    >
      {#if data && data.chats}
        {#each data.chats as chat (chat.id)}
          <li in:fly={{ x: -100, duration: 900 }}>
            <a
              href={"/chat/" + chat.id}
              class="group hover:from-base-100 hover:text-base-content flex items-center rounded-lg py-2 pl-2 text-base font-normal hover:bg-gradient-to-r hover:to-transparent"
              class:bg-base-300={id === chat.id}
            >
              <div class="flex w-full flex-col">
                <div class="flex w-full flex-col items-start justify-start">
                  <div
                    class="relative flex w-full flex-row items-center justify-between"
                  >
                    <div class="flex flex-col">
                      <p class="text-sm font-light">
                        {truncate(chat.subtitle, 42)}
                      </p>
                      <span class="text-xs font-semibold">{chat.model}</span>
                      <span class="text-xs"
                        >{timeSince(chat.created) + " ago"}</span
                      >
                    </div>
                    <div
                      class="absolute right-0 opacity-0 group-hover:opacity-100 transition"
                    >
                      <!-- {#if $page.params.id === chat.id} -->
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
                      <!-- {/if} -->
                    </div>
                  </div>
                </div>
              </div>
            </a>
          </li>
        {/each}
      {/if}
    </ul>
    <div class="w-full border-t border-base-content/[.2] pt-1">
      {#if deleteAllConfirm}
        <button
          class="btn btn-ghost w-full flex flex-row justify-between items-center p-2.5 text-left text-sm capitalize"
        >
          <div class="h-6 flex flex-row items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 16 16"
              width="18"
              height="18"
              fill="currentColor"
              class="mr-3"
            >
              <path
                d="M11 1.75V3h2.25a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1 0-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75ZM4.496 6.675l.66 6.6a.25.25 0 0 0 .249.225h5.19a.25.25 0 0 0 .249-.225l.66-6.6a.75.75 0 0 1 1.492.149l-.66 6.6A1.748 1.748 0 0 1 10.595 15h-5.19a1.75 1.75 0 0 1-1.741-1.575l-.66-6.6a.75.75 0 1 1 1.492-.15ZM6.5 1.75V3h3V1.75a.25.25 0 0 0-.25-.25h-2.5a.25.25 0 0 0-.25.25Z"
              >
              </path>
            </svg>
            <span>Clear Chats</span>
          </div>
          <div class="h-6 flex flex-row items-center">
            <button
              name="confirm-delete"
              class="btn-ghost btn-sm btn"
              on:click|preventDefault={() => deleteAllChat()}
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
              on:click|preventDefault={toggleDeleteAllConfirm}
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
        </button>
      {:else}
        <button
          on:click|preventDefault={toggleDeleteAllConfirm}
          class="btn btn-ghost w-full flex justify-start items-center p-2.5 text-left text-sm capitalize"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16"
            width="18"
            height="18"
            fill="currentColor"
            class="mr-3"
          >
            <path
              d="M11 1.75V3h2.25a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1 0-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75ZM4.496 6.675l.66 6.6a.25.25 0 0 0 .249.225h5.19a.25.25 0 0 0 .249-.225l.66-6.6a.75.75 0 0 1 1.492.149l-.66 6.6A1.748 1.748 0 0 1 10.595 15h-5.19a1.75 1.75 0 0 1-1.741-1.575l-.66-6.6a.75.75 0 1 1 1.492-.15ZM6.5 1.75V3h3V1.75a.25.25 0 0 0-.25-.25h-2.5a.25.25 0 0 0-.25.25Z"
            >
            </path>
          </svg>
          <span>Clear Chats</span>
        </button>
      {/if}
      <button
        on:click={toggleTheme}
        class="btn btn-ghost w-full flex justify-start items-center p-2.5 text-left text-sm capitalize"
      >
        <label class="swap swap-rotate" for="theme-toggle">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16"
            width="18"
            height="18"
            fill="currentColor"
            class={`mr-3 ${theme == "dark" ? "swap-on" : "swap-off"}`}
          >
            <path
              d="M8 12a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm0-1.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Zm5.657-8.157a.75.75 0 0 1 0 1.061l-1.061 1.06a.749.749 0 0 1-1.275-.326.749.749 0 0 1 .215-.734l1.06-1.06a.75.75 0 0 1 1.06 0Zm-9.193 9.193a.75.75 0 0 1 0 1.06l-1.06 1.061a.75.75 0 1 1-1.061-1.06l1.06-1.061a.75.75 0 0 1 1.061 0ZM8 0a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0V.75A.75.75 0 0 1 8 0ZM3 8a.75.75 0 0 1-.75.75H.75a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 3 8Zm13 0a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1 0-1.5h1.5A.75.75 0 0 1 16 8Zm-8 5a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5A.75.75 0 0 1 8 13Zm3.536-1.464a.75.75 0 0 1 1.06 0l1.061 1.06a.75.75 0 0 1-1.06 1.061l-1.061-1.06a.75.75 0 0 1 0-1.061ZM2.343 2.343a.75.75 0 0 1 1.061 0l1.06 1.061a.751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018l-1.06-1.06a.75.75 0 0 1 0-1.06Z"
            >
            </path>
          </svg>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16"
            width="18"
            height="18"
            fill="currentColor"
            class={`mr-3 ${theme == "dark" ? "swap-off" : "swap-on"}`}
          >
            <path
              d="M9.598 1.591a.749.749 0 0 1 .785-.175 7.001 7.001 0 1 1-8.967 8.967.75.75 0 0 1 .961-.96 5.5 5.5 0 0 0 7.046-7.046.75.75 0 0 1 .175-.786Zm1.616 1.945a7 7 0 0 1-7.678 7.678 5.499 5.499 0 1 0 7.678-7.678Z"
            >
            </path>
          </svg>
        </label>
        <span>{theme == "dark" ? "Light" : "Dark"} theme</span>
      </button>
      <a
        href="/"
        class="btn btn-ghost w-full flex justify-start items-center p-2.5 text-left text-sm capitalize"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 16 16"
          width="18"
          height="18"
          fill="currentColor"
          class="mr-3"
        >
          <path
            d="M8 0a8.2 8.2 0 0 1 .701.031C9.444.095 9.99.645 10.16 1.29l.288 1.107c.018.066.079.158.212.224.231.114.454.243.668.386.123.082.233.09.299.071l1.103-.303c.644-.176 1.392.021 1.82.63.27.385.506.792.704 1.218.315.675.111 1.422-.364 1.891l-.814.806c-.049.048-.098.147-.088.294.016.257.016.515 0 .772-.01.147.038.246.088.294l.814.806c.475.469.679 1.216.364 1.891a7.977 7.977 0 0 1-.704 1.217c-.428.61-1.176.807-1.82.63l-1.102-.302c-.067-.019-.177-.011-.3.071a5.909 5.909 0 0 1-.668.386c-.133.066-.194.158-.211.224l-.29 1.106c-.168.646-.715 1.196-1.458 1.26a8.006 8.006 0 0 1-1.402 0c-.743-.064-1.289-.614-1.458-1.26l-.289-1.106c-.018-.066-.079-.158-.212-.224a5.738 5.738 0 0 1-.668-.386c-.123-.082-.233-.09-.299-.071l-1.103.303c-.644.176-1.392-.021-1.82-.63a8.12 8.12 0 0 1-.704-1.218c-.315-.675-.111-1.422.363-1.891l.815-.806c.05-.048.098-.147.088-.294a6.214 6.214 0 0 1 0-.772c.01-.147-.038-.246-.088-.294l-.815-.806C.635 6.045.431 5.298.746 4.623a7.92 7.92 0 0 1 .704-1.217c.428-.61 1.176-.807 1.82-.63l1.102.302c.067.019.177.011.3-.071.214-.143.437-.272.668-.386.133-.066.194-.158.211-.224l.29-1.106C6.009.645 6.556.095 7.299.03 7.53.01 7.764 0 8 0Zm-.571 1.525c-.036.003-.108.036-.137.146l-.289 1.105c-.147.561-.549.967-.998 1.189-.173.086-.34.183-.5.29-.417.278-.97.423-1.529.27l-1.103-.303c-.109-.03-.175.016-.195.045-.22.312-.412.644-.573.99-.014.031-.021.11.059.19l.815.806c.411.406.562.957.53 1.456a4.709 4.709 0 0 0 0 .582c.032.499-.119 1.05-.53 1.456l-.815.806c-.081.08-.073.159-.059.19.162.346.353.677.573.989.02.03.085.076.195.046l1.102-.303c.56-.153 1.113-.008 1.53.27.161.107.328.204.501.29.447.222.85.629.997 1.189l.289 1.105c.029.109.101.143.137.146a6.6 6.6 0 0 0 1.142 0c.036-.003.108-.036.137-.146l.289-1.105c.147-.561.549-.967.998-1.189.173-.086.34-.183.5-.29.417-.278.97-.423 1.529-.27l1.103.303c.109.029.175-.016.195-.045.22-.313.411-.644.573-.99.014-.031.021-.11-.059-.19l-.815-.806c-.411-.406-.562-.957-.53-1.456a4.709 4.709 0 0 0 0-.582c-.032-.499.119-1.05.53-1.456l.815-.806c.081-.08.073-.159.059-.19a6.464 6.464 0 0 0-.573-.989c-.02-.03-.085-.076-.195-.046l-1.102.303c-.56.153-1.113.008-1.53-.27a4.44 4.44 0 0 0-.501-.29c-.447-.222-.85-.629-.997-1.189l-.289-1.105c-.029-.11-.101-.143-.137-.146a6.6 6.6 0 0 0-1.142 0ZM11 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM9.5 8a1.5 1.5 0 1 0-3.001.001A1.5 1.5 0 0 0 9.5 8Z"
          >
          </path>
        </svg>
        <span>Settings</span>
      </a>
    </div>
  </div>
</aside>

<button class="h-full w-full" on:click={hideSidebar} type="button">
  <slot />
</button>
