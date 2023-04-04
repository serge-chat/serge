<script lang="ts">
  import type { PageData } from "./$types";
  import { invalidate } from "$app/navigation";
  import { page } from "$app/stores";

  export let data: PageData;

  $: isLoading = false;
  $: questions = data.props.questions ?? [];
  $: startDate = new Date(data.props.created);

  $: prompt = "";
  $: answer = "";

  async function askQuestion() {
    if (prompt) {
      const data = new URLSearchParams();
      data.append("prompt", prompt);

      const eventSource = new EventSource(
        "/api/chat/" + $page.params.id + "/question?" + data.toString()
      );

      questions = [
        ...questions,
        {
          _id: (questions.length + 1).toString(),
          question: prompt,
          answer: "",
        },
      ];

      prompt = "";

      eventSource.addEventListener("message", (event) => {
        questions[questions.length - 1].answer += event.data;
      });

      eventSource.addEventListener("close", async () => {
        eventSource.close();
        await invalidate("/api/chat/" + $page.params.id);
      });

      eventSource.onerror = async (error) => {
        eventSource.close();
        questions[questions.length - 1].answer = "A server error occurred.";
        await invalidate("/api/chat/" + $page.params.id);
      };
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && event.ctrlKey) {
      askQuestion();
    }
  }

  function createSameSession(sessionID) {
    fetch("/api/chat/" + sessionID)
      .then((response) => response.json())
      .then((data) => {
        const { _id, created, parameters } = data;
        fetch(
          `/api/chat/?model=${parameters.model}&temperature=${parameters.temperature}&top_k=${parameters.top_k}&top_p=${parameters.top_p}&max_length=${parameters.max_length}&context_window=${parameters.context_window}&repeat_last_n=${parameters.repeat_last_n}&repeat_penalty=${parameters.repeat_penalty}&init_prompt=${parameters.init_prompt}&n_threads=${parameters.n_threads}`,
          {
            method: "POST",
            headers: {
              accept: "application/json",
            },
          }
        )
          .then((response) => response.json())
          .then((data) => {
            const newSession = { id: data };
            window.location.href = "/chat/" + newSession.id;
          });
      })
      .catch((error) => console.error(error));
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "n" && event.altKey) {
      createSameSession($page.params.id);
    }
  });
</script>

<div
  class="max-w-4xl mx-auto h-full max-h-screen relative"
  on:keydown={handleKeyDown}
>
  <h1 class="text-4xl font-bold">Chat with {data.props.parameters.model}</h1>
  <h4 class="text-xl font-semibold mb-10">
    Started on {startDate.toLocaleString("en-US")}
  </h4>
  <div class="overflow-y-auto h-[calc(100vh-12rem)] px-10 mb-11">
    <div class="h-max pb-32">
      {#each questions as question}
        <div class="chat chat-end my-2">
          <div
            class="chat-bubble chat-bubble-secondary whitespace-pre-line text-lg"
          >
            {question.question}
          </div>
        </div>
        <div class="chat chat-start my-2">
          <div
            class="chat-bubble chat-bubble-primary whitespace-pre-line text-lg"
          >
            {#if question.error}
              A server error occurred. See below:
              <div class="font-mono font-thin text-sm text-gray-100 pt-5">
                {question.error}
              </div>
            {:else}
              {#if question.answer === ""}
                <div
                  class="radial-progress animate-spin"
                  style="--value:70; --size:2rem;"
                />
              {/if}
              {question.answer}
            {/if}
          </div>
        </div>
      {/each}
    </div>
  </div>
  <div
    class="items-center w-full px-0 h-0 flex flex-row bg-base-100 justify-center"
  >
    <textarea
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
    <button
      type="button"
      disabled={isLoading}
      class="btn btn-primary h-10 w-24 text-lg ml-2 mb-5"
      class:loading={isLoading}
      on:click|preventDefault={() => createSameSession($page.params.id)}
    >
      New
    </button>
  </div>
</div>
