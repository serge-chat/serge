<script lang="ts">
  import { navigating } from "$app/stores";
  import type { PageData } from "./$types";
  import { enhance } from "$app/forms";

  export let data: PageData;

  $: isLoading = false;
  $: questions = data.props.questions ?? [];
  $: startDate = new Date(data.props.created);
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
            {question.answer}
          </div>
        </div>
      {/each}
    </div>
  </div>

  <form
    method="POST"
    class="form-control items-center absolute bottom-0 w-full px-5 left-0 h-32 flex flex-row bg-base-100"
    use:enhance={() => {
      isLoading = true;

      return async ({ update }) => {
        isLoading = false;
        update();
      };
    }}
  >
    <textarea
      name="question"
      class="textarea textarea-bordered h-24 w-full text-lg"
      placeholder="Why is the sky blue?"
      disabled={isLoading}
    />
    <button
      type="submit"
      disabled={isLoading}
      class={"btn btn-primary max-w-lg m-3 h-24 w-24 text-lg"}
      class:loading={isLoading}
    >
      Send
    </button>
  </form>
</div>
