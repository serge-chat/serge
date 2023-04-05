<script lang="ts">
  import type { PageData } from "./$types";
  import { invalidate } from "$app/navigation";
  import { page } from "$app/stores";
  import { browser } from "$app/environment";

  export let data: PageData;
  let clear: number;

  $: isLoading = false;
  $: questions = data.props.questions ?? [];
  $: startDate = new Date(data.props.created);

  $: prompt = "";

  $: if (browser) {
    void fetch("/api/chat/" + $page.params.id + "/status")
      .then((r) => r.json())
      .then((data) => {
        if (data === "streaming") {
          void streamPage();
        }
      });
  }

  const streamPage = async () => {
    const requestStream = await fetch(
      "/api/chat/" + $page.params.id + "/stream"
    );

    const dataStream = await requestStream.json();

    if (dataStream.answer === "EOF") {
      await invalidate("/api/chat/" + $page.params.id);
      return;
    } else {
      if (
        questions.length > 0 &&
        questions[questions.length - 1]._id === "STREAM"
      ) {
        questions[questions.length - 1].question = dataStream.question;
        questions[questions.length - 1].answer = dataStream.answer;
      } else {
        questions = [
          ...questions,
          {
            _id: "STREAM",
            question: dataStream.question,
            answer: dataStream.answer,
          },
        ];
      }
    }

    setTimeout(streamPage, 500);
  };

  const askQuestion = async () => {
    if (prompt) {
      const params = new URLSearchParams();
      params.append("prompt", prompt);

      isLoading = true;
      const r = await fetch(
        "/api/chat/" + $page.params.id + "/question?" + params.toString(),
        {
          method: "POST",
        }
      );

      isLoading = false;
      prompt = "";
      await streamPage();
    }
  };

  async function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter" && event.ctrlKey) {
      await askQuestion();
    }
  }
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
  </div>
</div>
