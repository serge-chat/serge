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
</script>

<div class="max-w-4xl mx-auto h-full max-h-screen relative">
  <h1 class="text-4xl font-bold">Chat with {data.props.parameters.model}</h1>
  <h4 class="text-xl font-semibold mb-10">
    Started on {startDate.toLocaleString("en-US")}
  </h4>

  <div class="overflow-y-auto h-[calc(100vh-10rem)] px-10">
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
    class="items-center absolute bottom-0 w-full px-5 left-0 h-32 flex flex-row bg-base-100"
  >
    <textarea
      name="question"
      class="textarea textarea-bordered h-24 w-full text-lg"
      disabled={isLoading}
      placeholder="Ask a question..."
      bind:value={prompt}
    />
    <button
      type="submit"
      disabled={isLoading}
      class={"btn btn-primary max-w-lg m-3 h-24 w-24 text-lg"}
      class:loading={isLoading}
      on:click|preventDefault={askQuestion}
    >
      Send
    </button>
  </div>
</div>
