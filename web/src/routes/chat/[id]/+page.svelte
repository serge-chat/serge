<script lang="ts">
  import { navigating } from "$app/stores";
  import type { PageData } from "./$types";

  export let data: PageData;

  const questions = data.props.questions ?? [];

  const startDate = new Date(data.props.created);
</script>

<div class="max-w-4xl mx-auto">
  <h1 class="text-4xl font-bold">Chat with {data.props.parameters.model}</h1>
  <h4 class="text-xl font-semibold mb-10">
    Started on {startDate.toLocaleString("en-US")}
  </h4>
  {#each questions as question}
    <div class="chat chat-end">
      <div class="chat-bubble chat-bubble-secondary whitespace-pre-line">
        {question.question}
      </div>
    </div>
    <div class="chat chat-start">
      <div class="chat-bubble chat-bubble-primary whitespace-pre-line">
        {question.answer}
      </div>
    </div>
  {/each}

  <form method="POST" class="form-control items-center mt-3">
    <textarea
      name="question"
      class="textarea textarea-bordered h-24 w-full"
      placeholder="Why is the sky blue?"
    />
    <button
      type="submit"
      class={"btn btn-primary max-w-lg m-3" + ($navigating ? "loading" : "")}
    >
      Send
    </button>
  </form>
</div>
