<script lang="ts">
  import type { PageData } from "./$types";
  import { invalidate, goto } from "$app/navigation";
  import { page } from "$app/stores";

  export let data: PageData;

  $: isLoading = false;
  $: startDate = new Date(data.chat.created);
  $: history = data.chat.history;

  $: prompt = "";

  async function askQuestion() {
    if (prompt) {
      const data = new URLSearchParams();
      data.append("prompt", prompt);

      const eventSource = new EventSource(
        "/api/chat/" + $page.params.id + "/question?" + data.toString()
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
      });

      eventSource.onerror = async (error) => {
        eventSource.close();
        history[history.length - 1].data.content = "A server error occurred.";
        await invalidate("/api/chat/" + $page.params.id);
      };
    }
  }

  async function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter" && event.ctrlKey) {
      await askQuestion();
    }
  }

  async function createSameSession() {
    const newData = await fetch(
      `/api/chat/?model=${data.chat.params.model_path}&temperature=${data.chat.params.temperature}&top_k=${data.chat.params.top_k}` +
        `&top_p=${data.chat.params.top_p}&max_length=${data.chat.params.max_tokens}&context_window=${data.chat.params.n_ctx}` +
        `&repeat_last_n=${data.chat.params.last_n_tokens_size}&repeat_penalty=${data.chat.params.repeat_penalty}` +
        `&n_threads=${data.chat.params.n_threads}&init_prompt=${data.chat.history[0].data.content}`,

      {
        method: "POST",
        headers: {
          accept: "application/json",
        },
      }
    ).then((response) => response.json());
    await invalidate("/api/chat/");
    await goto("/chat/" + newData);
  }

  document.addEventListener("keydown", async (event) => {
    if (event.key === "n" && event.altKey) {
      await createSameSession();
    }
  });
</script>

<div
  class="max-w-4xl mx-auto h-full max-h-screen relative"
  on:keydown={handleKeyDown}
>
  <div class="flex items-center">
    <h1 class="text-4xl font-bold inline-block mr-2">
      Chat with {data.chat.params.model_path}
    </h1>
    <div
      class="tooltip tooltip-bottom"
      data-tip="This will create a new chat session with the same parameters."
    >
      <button
        type="button"
        disabled={isLoading}
        class="btn btn-sm mr-2 mt-5 mb-5 inline-block"
        class:loading={isLoading}
        on:click|preventDefault={() => createSameSession()}
      >
        New
      </button>
    </div>
  </div>
  <h4 class="text-xl font-semibold mb-5">
    Started on {startDate.toLocaleString("en-US")}
  </h4>
  <div class="overflow-y-auto h-[calc(97vh-12rem)] px-10 mb-11">
    <div class="h-max pb-32">
      {#each history as question}
        {#if question.type === "human"}
          <div class="chat chat-end my-2">
            <div
              class="chat-bubble chat-bubble-secondary whitespace-pre-line text-lg"
            >
              {question.data.content}
            </div>
          </div>
        {:else if question.type === "ai"}
          <div class="chat chat-start my-2">
            <div
              class="chat-bubble chat-bubble-primary whitespace-pre-line text-lg"
            >
              {#if question.data.content === ""}
                <div
                  class="radial-progress animate-spin"
                  style="--value:70; --size:2rem;"
                />
              {/if}
              {question.data.content}
            </div>
          </div>
        {:else if question.type === "system"}
          <div
            class="w-full text-center font-light text-md text-gray-500 pb-10"
          >
            {question.data.content}
          </div>
        {/if}
      {/each}
    </div>
  </div>
  <div
    class="items-center w-full px-0 h-0 flex flex-row bg-base-100 justify-center"
  >
    <textarea
      autofocus
      name="question"
      class="textarea textarea-bordered h-10 w-full max-w-xl mb-5 text-lg"
      disabled={isLoading}
      placeholder="Ask a question..."
      bind:value={prompt}
    />
    <button
      type="submit"
      disabled={isLoading}
      class="btn btn-primary h-10 w-24 text-lg ml-2 mb-5"
      class:loading={isLoading}
      on:click|preventDefault={askQuestion}
    >
      Send
    </button>
  </div>
</div>
