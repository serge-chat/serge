<script lang="ts">
  import type { PageData } from "./$types";
  import { invalidate, goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { newChat, themeStore } from "$lib/stores";
  import { onMount, onDestroy } from "svelte";
  import ClipboardJS from "clipboard";
  import hljs from "highlight.js";
  import "highlight.js/styles/github-dark.css";
  import bash from "highlight.js/lib/languages/bash";
  import css from "highlight.js/lib/languages/css";
  import cpp from "highlight.js/lib/languages/cpp";
  import dockerfile from "highlight.js/lib/languages/dockerfile";
  import go from "highlight.js/lib/languages/go";
  import javascript from "highlight.js/lib/languages/javascript";
  import json from "highlight.js/lib/languages/json";
  import ini from "highlight.js/lib/languages/ini";
  import nginx from "highlight.js/lib/languages/nginx";
  import plaintext from "highlight.js/lib/languages/plaintext";
  import powershell from "highlight.js/lib/languages/powershell";
  import python from "highlight.js/lib/languages/python";
  import rust from "highlight.js/lib/languages/rust";
  import swift from "highlight.js/lib/languages/swift";
  import sql from "highlight.js/lib/languages/sql";
  import typescript from "highlight.js/lib/languages/typescript";
  import html from "highlight.js/lib/languages/xml";
  import yaml from "highlight.js/lib/languages/yaml";
  import MarkdownIt from "markdown-it";
  import mdHighlight from "markdown-it-highlightjs";

  hljs.registerLanguage("bash", bash);
  hljs.registerLanguage("css", css);
  hljs.registerLanguage("cpp", cpp);
  hljs.registerLanguage("dockerfile", dockerfile);
  hljs.registerLanguage("go", go);
  hljs.registerLanguage("javascript", javascript);
  hljs.registerLanguage("json", json);
  hljs.registerLanguage("ini", ini);
  hljs.registerLanguage("nginx", nginx);
  hljs.registerLanguage("plaintext", plaintext);
  hljs.registerLanguage("powershell", powershell);
  hljs.registerLanguage("python", python);
  hljs.registerLanguage("rust", rust);
  hljs.registerLanguage("sql", sql);
  hljs.registerLanguage("swift", swift);
  hljs.registerLanguage("typescript", typescript);
  hljs.registerLanguage("xml", html);
  hljs.registerLanguage("yaml", yaml);

  export let data: PageData;
  let messageContainer: any;
  let theme: string;
  let styleElement: HTMLLinkElement;
  const isLoading = false;
  $: startDate = new Date(data.chat.created);
  $: history = data.chat.history;
  $: newChat.set(data.chat);
  $: if (messageContainer) {
    messageContainer.scrollBottom = messageContainer.scrollHeight;
  }
  let prompt = "";

  async function askQuestion() {
    const data = new URLSearchParams();

    if (!prompt || prompt === "") {
      prompt = "Reformulate your last answer.";
    }

    data.append("prompt", prompt);

    const eventSource = new EventSource(
      "/api/chat/" + $page.params.id + "/question?" + data.toString(),
    );

    history = [
      ...history,
      {
        type: "human",
        data: {
          content: prompt,
        },
      },
      {
        type: "ai",
        data: {
          content: "",
        },
      },
    ];

    prompt = "";

    eventSource.addEventListener("message", (event) => {
      history[history.length - 1].data.content += event.data;
    });

    eventSource.addEventListener("close", async () => {
      eventSource.close();
      await invalidate("/api/chat/" + $page.params.id);
      prompt = "";
    });

    eventSource.onerror = async (error) => {
      eventSource.close();
    };
  }

  async function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      await askQuestion();
    }
  }

  async function createSameSession() {
    const newData = await fetch(
      `/api/chat/?model=${data.chat.params.model_path}&temperature=${data.chat.params.temperature}&top_k=${data.chat.params.top_k}` +
        `&top_p=${data.chat.params.top_p}&max_length=${data.chat.params.max_tokens}&context_window=${data.chat.params.n_ctx}` +
        `&repeat_last_n=${data.chat.params.last_n_tokens_size}&repeat_penalty=${data.chat.params.repeat_penalty}` +
        `&n_threads=${data.chat.params.n_threads}&init_prompt=${data.chat.history[0].data.content}` +
        `&gpu_layers=${data.chat.params.n_gpu_layers}`,

      {
        method: "POST",
        headers: {
          accept: "application/json",
        },
      },
    ).then((response) => response.json());
    await invalidate("/api/chat/");
    await goto("/chat/" + newData);
  }

  async function deletePrompt(chatID: string, idx: number) {
    const response = await fetch(
      `/api/chat/${chatID}/prompt?idx=${idx.toString()}`,
      { method: "DELETE" },
    );

    if (response.status === 200) {
      await invalidate("/api/chat/" + $page.params.id);
    } else if (response.status === 202) {
      showToast("Chat in progress!");
    } else {
      showToast("An error occurred: " + response.statusText);
    }
  }

  function showToast(message: string) {
    // Create the toast element
    const toast = document.createElement("div");
    toast.className = `alert alert-info`;
    toast.textContent = message;
    const toastContainer = document.getElementById("toast-container");

    // Append the toast to the toast container if it exists
    if (toastContainer) {
      toastContainer.appendChild(toast);
    } else {
      console.error("Toast container not found?");
      return;
    }

    // Automatically remove the toast after a delay
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }

  const md: MarkdownIt = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true,
    highlight: (code_string: string, lang: string) => {
      if (lang && hljs.getLanguage(lang)) {
        try {
          const code = hljs.highlight(code_string, lang).value;
          return hljs.highlight(code, { language: lang }).value;
        } catch (ex) {
          /**/
        }
      }
      return "";
    },
  }).use(mdHighlight, { hljs });

  const originalFenceRenderer = md.renderer.rules.fence;

  md.renderer.rules.fence = (
    tokens: any,
    index: any,
    options: any,
    env: any,
    self: any,
  ) => {
    // Increment the codeblock id
    const id = `code-block-${Math.random().toString(36).substring(7)}`;
    // Generate original fenced code block HTML
    if (!originalFenceRenderer)
      throw new Error("originalFenceRenderer is undefined");
    // Create copy button HTML
    const copyButton = `<div class="tooltip tooltip-top absolute top-0.5 right-1" data-tip="copy"><button class="btn btn-xs btn-square btn-ghost copy-button" data-clipboard-target="#${id}"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="12" height="12"><path class="fill-base-content" d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z"></path><path class="fill-base-content" d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"></path></svg></button></div>`;

    const codeBlock = originalFenceRenderer(tokens, index, options, env, self)
      .replace(`<code `, `<code id="${id}"`)
      .replace(
        `<pre>`,
        `<pre class="relative max-w-7xl mx-auto">${copyButton}`,
      );

    // Get the token and code content
    const token = tokens[index];
    const content = token.content;

    // Wrap the fenced code block and copy button in a container
    const html = `
      ${codeBlock}
    `;

    return html;
  };

  const renderMarkdown = (q: any) => {
    return md.render(q);
  };

  onMount(() => {
    styleElement = document.createElement("link");
    styleElement.rel = "stylesheet";
    const cbJS = new ClipboardJS(".copy-button");
    newChat.set(data.chat);
    updateThemeStyle($themeStore);
    themeStore.subscribe((newTheme) => {
      updateThemeStyle(newTheme);
    });

    document.addEventListener("keydown", async (event) => {
      if (event.key === "n" && event.altKey) {
        await createSameSession();
      }
    });
  });

  function updateThemeStyle(currentTheme: string) {
    if (currentTheme === "dark") {
      styleElement.href = "/css/github-dark.css";
    } else {
      styleElement.href = "/css/github.css";
    }
    document.head.appendChild(styleElement);
  }

  let sendBottomHovered = false;
  const onMouseEnter = () => {
    sendBottomHovered = true;
  };
  const onMouseLeave = () => {
    sendBottomHovered = false;
  };
  const scrollToBottom = (node: Element, history: any[]) => {
    const scroll = () =>
      node.scroll({
        top: node.scrollHeight,
        behavior: "smooth",
      });
    scroll();

    return { update: scroll };
  };
  onDestroy(() => {
    styleElement && styleElement.remove();
  });
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
  class="relative h-full max-h-screen overflow-hidden"
  on:keydown={handleKeyDown}
>
  <div class="mx-20">
    <div class="h-8 justify-content border-b border-base-content/[.2]">
      <div class="h-full relative flex items-center justify-center">
        <div
          class="flex flex-row items-center justify-center color-base-300"
          title="Model"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 11.12744 16"
            class="w-4 h-4 fill-base-content"
          >
            <path
              d="M11.15892,3.83508l.9569,3.28975L11.244,6.93678l-.08509-3.1017M8.975,9.14916l.05544,2.01865-1.55571-.04563.4741-1.86674L8.975,9.14916m2.33481.1842.94357.20353-.58466,1.70826-.30671-.009-.0522-1.9028M5.481,9.511l-.24516.96492-.68826-.39155.21013-.49843L5.481,9.511M10.5126,0l-.43806.77407.02067.75242L10.535.9551,10.5126,0Zm.26454,1.17968-.557.72373,1.82091.64863,1.49262-.69661-.34745-.50351-2.4091-.17224Zm-.66306,1.03474.15184,5.53439,3.27854.70718L11.91558,2.856l-1.8015-.64162ZM9.945,8.04335l-2.79356.28933-.953,3.7525,3.86072.11323L9.945,8.04335Zm.33025.04387.11305,4.12083,1.98787.05827,1.18754-3.4698-3.28846-.7093ZM6.803,8.36864h0Zm0,0-2.73689.28355-.785,1.86212L5.882,11.99393,6.803,8.36864Zm-3.179.486h0Zm0,0-1.18773.96908.73231.11109L3.624,8.85465Zm-.38665,2.013v2.79493H4.288L5.71641,12.278l-2.479-1.41032Zm7.16,1.66978L10.49236,16h.60594l1.16636-3.40782-1.8673-.05475Zm-6.16877,1.454H3.31036L4.06615,16h.70229l-.53985-2.00859Z"
              transform="translate(-2.43628)"
            />
          </svg>
          <span class="ml-2 inline-block text-center text-sm font-semibold">
            {data.chat.params.model_path}
          </span>
        </div>
        <div
          class="pl-4 hidden sm:flex flex-row items-center justify-center"
          title="Temperature"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 5.31286 16"
            class="w-3.5 h-3.5 fill-base-content"
          >
            <path
              d="M10.65643,13.34357a2.55061,2.55061,0,0,1-.77092,1.901A2.59167,2.59167,0,0,1,8,16a2.59167,2.59167,0,0,1-1.88551-.75544,2.55061,2.55061,0,0,1-.77092-1.901A2.52457,2.52457,0,0,1,6.39,11.21347V1.57281A1.51713,1.51713,0,0,1,6.84826.45822,1.558,1.558,0,0,1,7.9969,0,1.558,1.558,0,0,1,9.14555.45822a1.51713,1.51713,0,0,1,.45822,1.11459v9.64066A2.57207,2.57207,0,0,1,10.65643,13.34357Zm-.52633,0a2.03829,2.03829,0,0,0-1.05267-1.87V1.57281A.979.979,0,0,0,8.74925.83594a1.0689,1.0689,0,0,0-1.50469,0,.979.979,0,0,0-.32819.73687v9.90073a2.16318,2.16318,0,0,0-.42725,3.37782,2.14151,2.14151,0,0,0,3.01867,0A2.05349,2.05349,0,0,0,10.1301,13.34357Zm-.52633,0a1.57129,1.57129,0,0,1-1.60687,1.61,1.57129,1.57129,0,0,1-1.60686-1.61,1.48237,1.48237,0,0,1,1.08363-1.50469V6.39649a.46385.46385,0,0,1,.52323-.52633.46385.46385,0,0,1,.52324.52633v5.44239A1.48237,1.48237,0,0,1,9.60377,13.34357Z"
              transform="translate(-5.34357)"
            />
          </svg>
          <span class="ml-2 inline-block text-center text-sm font-semibold">
            {data.chat.params.temperature}
          </span>
        </div>
        <div
          class="pl-4 hidden sm:flex flex-row items-center justify-center"
          title="Context Length/Maximum Generated Tokens"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16"
            class="w-3.5 h-3.5 fill-base-content rotate-90"
          >
            <path
              d="M5.22 14.78a.75.75 0 0 0 1.06-1.06L4.56 12h8.69a.75.75 0 0 0 0-1.5H4.56l1.72-1.72a.75.75 0 0 0-1.06-1.06l-3 3a.75.75 0 0 0 0 1.06l3 3Zm5.56-6.5a.75.75 0 1 1-1.06-1.06l1.72-1.72H2.75a.75.75 0 0 1 0-1.5h8.69L9.72 2.28a.75.75 0 0 1 1.06-1.06l3 3a.75.75 0 0 1 0 1.06l-3 3Z"
            >
            </path>
          </svg>
          <span class="ml-2 inline-block text-center text-sm font-semibold">
            {data.chat.params.n_ctx}/{data.chat.params.max_tokens}
          </span>
        </div>
        {#if data.chat.params.n_threads > 0}
          <div
            class="pl-4 hidden sm:flex flex-row items-center justify-center"
            title="Threads"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-4 h-4"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z"
              />
            </svg>
            <span class="ml-2 inline-block text-center text-sm font-semibold">
              {data.chat.params.n_threads}
            </span>
          </div>
        {/if}
        {#if data.chat.params.n_gpu_layers > 0}
          <div
            class="pl-4 hidden sm:flex flex-row items-center justify-center"
            title="GPU Layers"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 16 16"
              class="w-3.5 h-3.5 fill-base-content"
            >
              <path
                d="M7.75 14A1.75 1.75 0 0 1 6 12.25v-8.5C6 2.784 6.784 2 7.75 2h6.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0 1 14.25 14Zm-.25-1.75c0 .138.112.25.25.25h6.5a.25.25 0 0 0 .25-.25v-8.5a.25.25 0 0 0-.25-.25h-6.5a.25.25 0 0 0-.25.25ZM4.9 3.508a.75.75 0 0 1-.274 1.025.249.249 0 0 0-.126.217v6.5c0 .09.048.173.126.217a.75.75 0 0 1-.752 1.298A1.75 1.75 0 0 1 3 11.25v-6.5c0-.649.353-1.214.874-1.516a.75.75 0 0 1 1.025.274ZM1.625 5.533h.001a.249.249 0 0 0-.126.217v4.5c0 .09.048.173.126.217a.75.75 0 0 1-.752 1.298A1.748 1.748 0 0 1 0 10.25v-4.5a1.748 1.748 0 0 1 .873-1.516.75.75 0 1 1 .752 1.299Z"
              >
              </path>
            </svg>
            <span class="ml-2 inline-block text-center text-sm font-semibold">
              {data.chat.params.n_gpu_layers}
            </span>
          </div>
        {/if}
        <div
          class="pl-4 hidden sm:flex flex-row items-center justify-center"
          title="Repeat Penalty"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16"
            class="w-3 h-3 fill-base-content"
          >
            <path
              d="M5.029 2.217a6.5 6.5 0 0 1 9.437 5.11.75.75 0 1 0 1.492-.154 8 8 0 0 0-14.315-4.03L.427 1.927A.25.25 0 0 0 0 2.104V5.75A.25.25 0 0 0 .25 6h3.646a.25.25 0 0 0 .177-.427L2.715 4.215a6.491 6.491 0 0 1 2.314-1.998ZM1.262 8.169a.75.75 0 0 0-1.22.658 8.001 8.001 0 0 0 14.315 4.03l1.216 1.216a.25.25 0 0 0 .427-.177V10.25a.25.25 0 0 0-.25-.25h-3.646a.25.25 0 0 0-.177.427l1.358 1.358a6.501 6.501 0 0 1-11.751-3.11.75.75 0 0 0-.272-.506Z"
            >
            </path>
            <path
              d="M9.06 9.06a1.5 1.5 0 1 1-2.12-2.12 1.5 1.5 0 0 1 2.12 2.12Z"
            >
            </path>
          </svg>
          <span class="ml-2 inline-block text-center text-sm font-semibold">
            {data.chat.params.repeat_penalty}
          </span>
        </div>
        <div
          class="pl-4 hidden sm:flex flex-row items-center justify-center"
          title="Top_k-Top_p"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 16 16"
            class="w-3 h-3 fill-base-content"
          >
            <path
              d="M6 2c.306 0 .582.187.696.471L10 10.731l1.304-3.26A.751.751 0 0 1 12 7h3.25a.75.75 0 0 1 0 1.5h-2.742l-1.812 4.528a.751.751 0 0 1-1.392 0L6 4.77 4.696 8.03A.75.75 0 0 1 4 8.5H.75a.75.75 0 0 1 0-1.5h2.742l1.812-4.529A.751.751 0 0 1 6 2Z"
            >
            </path>
          </svg>
          <span class="ml-2 inline-block text-center text-sm font-semibold">
            {`${data.chat.params.top_k}-${data.chat.params.top_p}`}
          </span>
        </div>
      </div>
    </div>
  </div>
  <div
    class="mb-11 h-[calc(98vh-10rem)] 2xl:h-[calc(97vh-12rem)] overflow-y-auto"
    use:scrollToBottom={history}
  >
    <div class="h-max pb-4">
      {#each history as question, i}
        {#if question.type === "human"}
          <div class="w-10/12 mx-auto sm:w-10/12 chat chat-end py-4">
            <div class="chat-image self-start pl-1 pt-1">
              <div
                class="mask mask-squircle online flex aspect-square w-8 items-center justify-center overflow-hidden bg-gradient-to-b from-primary to-primary-focus"
              >
                <span class="text-xs text-neutral-content">I</span>
              </div>
            </div>
            <div
              class="chat-bubble whitespace-normal break-words bg-base-300 text-base font-light text-base-content"
            >
              <!-- {question.data.content} -->
              <div class="w-full overflow-hidden break-words">
                {@html renderMarkdown(question.data.content)}
              </div>
            </div>
            {#if i === history.length - 1 && !isLoading}
              <div style="width: 100%; text-align: right;">
                <button
                  disabled={isLoading}
                  class="btn-ghost btn-sm btn"
                  on:click|preventDefault={() => deletePrompt(data.chat.id, i)}
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
              </div>
            {/if}
          </div>
        {:else if question.type === "ai"}
          <div class="w-10/12 mx-auto sm:w-10/12 chat chat-start py-4">
            <div class="chat-image self-start pl-1 pt-1">
              <div
                class="mask mask-squircle online flex aspect-square w-8 items-center justify-center overflow-hidden bg-gradient-to-b from-primary to-primary-focus"
              >
                <span class="text-xs text-neutral-content">
                  {data.chat.params.model_path.substring(0, 1).toUpperCase()}
                </span>
              </div>
            </div>
            <div
              class="chat-bubble whitespace-normal bg-base-100 text-base font-light text-base-content w-full"
            >
              {#if question.data.content === ""}
                <div class="inline-block rounded bg-base-200 px-4 py-1">
                  <div class="dots-load aspect-square w-2 rounded-full" />
                </div>
              {/if}
              <!-- {question.data.content} -->
              <div class="markdown">
                {@html renderMarkdown(question.data.content)}
              </div>
            </div>
            {#if i === history.length - 1 && !isLoading}
              <div style="width: 100%; text-align: right;">
                <button
                  disabled={isLoading}
                  class="btn-ghost btn-sm btn"
                  on:click|preventDefault={() => deletePrompt(data.chat.id, i)}
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
                  <span class="sr-only">Delete</span>
                </button>
              </div>
            {/if}
          </div>
        {:else if question.type === "system"}
          <div
            class="text-md w-full px-10 pt-2 pb-4 text-center font-light md:px-16"
          >
            <h4 class="badge badge-ghost text-center text-xs font-semibold">
              {startDate.toLocaleString("en-US")}
            </h4>
            <br />
            {question.data.content}
          </div>
        {/if}
      {/each}
    </div>
  </div>
  <div
    class="flex h-0 w-full flex-row items-center justify-center bg-gradient-to-t from-indigo-500 px-0"
  >
    <div
      class="input-bordered input flex h-auto w-full max-w-3xl flex-row items-center justify-between rounded-lg bg-base-200 px-0 drop-shadow-md"
    >
      <textarea
        name="question"
        class="textarea h-10 flex-1 resize-y bg-[transparent] text-lg placeholder-base-content outline-0 ring-0 focus:outline-0"
        disabled={isLoading}
        placeholder="Message Serge..."
        bind:value={prompt}
      />
      <button
        on:mouseenter={onMouseEnter}
        on:mouseleave={onMouseLeave}
        type="submit"
        disabled={isLoading}
        class="btn btn-ghost h-10 w-14 rounded-l-none rounded-r-lg border-0 text-lg"
        class:loading={isLoading}
        on:click|preventDefault={askQuestion}
        ><span class="sr-only">Send</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 16 16"
          width="16"
          height="16"
        >
          <path
            class:fill-primary-content={sendBottomHovered}
            class:fill-base-content={!sendBottomHovered}
            d="M.989 8 .064 2.68a1.342 1.342 0 0 1 1.85-1.462l13.402 5.744a1.13 1.13 0 0 1 0 2.076L1.913 14.782a1.343 1.343 0 0 1-1.85-1.463L.99 8Zm.603-5.288L2.38 7.25h4.87a.75.75 0 0 1 0 1.5H2.38l-.788 4.538L13.929 8Z"
          />
        </svg>
      </button>
    </div>
  </div>
  <div id="toast-container" class="toast">
    <!-- Toast notifications will be added here -->
  </div>
</div>
