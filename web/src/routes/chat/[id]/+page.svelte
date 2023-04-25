<script lang="ts">
  import type { PageData } from "./$types";
  import { invalidate, goto } from "$app/navigation";
  import { page } from "$app/stores";

  export let data: PageData;

  $: isLoading = false;
  $: startDate = new Date(data.chat.created);
  $: history = data.chat.history;

  $: prompt = "";
  let container;

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

  let sendBottomHovered = false;
  const onMouseEnter = () => {
    sendBottomHovered = true;
  }
  const onMouseLeave = () => {
    sendBottomHovered = false;
  };
</script>

<div
  class="w-full mx-auto h-full max-h-screen relative overflow-hidden"
  on:keydown={handleKeyDown}
>
  <div class="w-full">
    <div class="flex justify-between items-center px-2 md:px-16">
      <a class="" href="https://github.com/nsarrazin/serge" target="_blank" rel="noopener noreferrer">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="24" height="24">
          <path class="fill-base-content" d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
        </svg>
      </a>
      <div class="flex flex-col justify-center items-center">
        <h1 class="text-center text-base font-bold inline-block">
          Serge: {data.chat.params.model_path}
        </h1>
        <h4 class="text-center text-xs font-semibold">
          {startDate.toLocaleString("en-US")}
        </h4>
      </div>
      <div
        class="tooltip tooltip-left"
        data-tip="This will create a new chat session with the same parameters."
      >
        <button
          type="button"
          disabled={isLoading}
          class="btn btn-sm inline-block"
          class:loading={isLoading}
          on:click|preventDefault={() => createSameSession()}
        >
          New
        </button>
      </div>
    </div>
    <div class="w-full border-t border-base-content opacity-20"></div>
  </div>
  <div class="overflow-y-auto h-[calc(97vh-12rem)] mb-11">
    <div class="h-max pb-32">
      {#each history as question}
        {#if question.type === "human"}
          <div class="w-full border-t border-base-content opacity-20"></div>
          <div class="chat chat-start px-10 md:px-16 py-4 bg-base-300">
            <div class="chat-image self-start avatar pl-1 pt-1">
              <div class="w-[2.6rem] bg-gradient-to-b from-primary to-primary-focus mask mask-squircle online">
                <svg class="my-2 mx-auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="24" height="24">
                  <path class="fill-base-200" d="M10.1,2.3l0.5-0.7l2.3,0.2l0.3,0.5l-1.4,0.7L10.1,2.3z M11.7,3.2L10,2.6l0.1,5.2l3.1,0.7L11.7,3.2z M10.1,8.1l0.1,3.9
                  l1.9,0.1l1.1-3.3L10.1,8.1z M10.4,0.5L9.9,1.2l0,0.7l0.4-0.5L10.4,0.5z M4.3,8.6l-0.7,1.7L6,11.7l0.9-3.4L4.3,8.6z M3.5,13.3h1
                  L5.9,12l-2.3-1.3V13.3z M2.8,9.7l0.7,0.1l0.4-1L2.8,9.7z M3.6,13.6l0.7,1.9H5l-0.5-1.9H3.6z M7.2,8.3l-0.9,3.5l3.6,0.1L9.8,8
                  L7.2,8.3z M10.3,15.5h0.6l1.1-3.2l-1.8-0.1L10.3,15.5z"/>
                </svg>
              </div>
            </div>
            <div
              class="chat-bubble bg-base-300 whitespace-pre-line text-base text-base-content font-light break-words"
            >
              {question.data.content}
            </div>
          </div>
        {:else if question.type === "ai"}
          <div class="w-full border-t border-base-content opacity-20"></div>
          <div class="chat chat-start px-10 md:px-16 py-4 bg-base-100">
            <div class="chat-image self-start avatar pl-1 pt-1">
              <div class="w-[2.6rem] bg-gradient-to-b from-primary to-primary-focus mask mask-squircle online">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="48" height="48">
                  <path class="stroke-base-300" fill="#c8b399" stroke-miterlimit="10" stroke-width="0.15px" d="M14.71526,15.15914q.15645-3.39789.2172-6.79948a.25392.25392,0,0,0-.0589-.16013L14.406,7.5921a.30419.30419,0,0,0-.34422-.11044q-.63133.2448-.74732-.02393a1.95718,1.95718,0,0,1-.14725-.554q-.10122-.87433-.64239-.74364a1.99586,1.99586,0,0,1-.54116.09019q-.52092-.10492-.4344-.80622.07916-.6387-.716-.762a.47745.47745,0,0,1-.4344-.43441,1.89641,1.89641,0,0,0-.416-.82278c-.11611-.15881-.23745-.05338-.23745-.05338q-.26872.37366-.27794.01105a.71088.71088,0,0,1,.02577-.18776A6.2486,6.2486,0,0,0,9.61842.61776a.67718.67718,0,0,0-1.19645,0,4.54511,4.54511,0,0,0-.66265,2.19777q-.0055.10492-.05153.01289a.56.56,0,0,1-.05339-.2669.10787.10787,0,0,0-.08282-.11412.849.849,0,0,0-.762.20984.34138.34138,0,0,0-.0902.15461.41776.41776,0,0,1-.66449.28715.23265.23265,0,0,0-.17118-.02025q-.26505.09572-.27058.5522-.00183.3663-.36262.29819-.66263-.127-.56876.497a.11856.11856,0,0,1-.09756.13621q-.94057.16382-.208.74.32766.25767-.04969.07914a10.54646,10.54646,0,0,0-1.55169-.58166,2.35641,2.35641,0,0,0-1.27192-.01472q-.68472.18039-.29266.78229a2.49922,2.49922,0,0,0,2.518,1.18356q.25953-.02577.138.081a.20376.20376,0,0,1-.13069.03129q-.12333-.00368-.1675.13989a5.33888,5.33888,0,0,0-.17855.74732.7172.7172,0,0,0,.34973.83566q.39023.20985.39207.21169a.71407.71407,0,0,1,.18407.70314.37974.37974,0,0,0,.36445.50986,1.17377,1.17377,0,0,1,.62766.2982.219.219,0,0,1,.06628.15645q.02208.61664.67921.532a.1806.1806,0,0,1,.15645.05153,1.402,1.402,0,0,1,.32948.62768.11491.11491,0,0,0,.11229.08467.62276.62276,0,0,1,.69026.53748.92728.92728,0,0,0,.15092.41231.59356.59356,0,0,0,.43625.19143.40358.40358,0,0,1,.43624.41231.71483.71483,0,0,0,.82831.74.73873.73873,0,0,1,.58718.29819.15558.15558,0,0,0,.14541.0497.638.638,0,0,1,.76572.31659.18671.18671,0,0,0,.18223.09941,1.26348,1.26348,0,0,1,1.11545.31475.13072.13072,0,0,0,.14173.03681.89878.89878,0,0,1,1.0087.18407.55982.55982,0,0,0,.79333.081q.3037-.22641.41416.13069l.41415.18407A5.85415,5.85415,0,0,1,14.71526,15.15914Z" transform="translate(-0.99243 -0.175)"/>
                  <path class="stroke-base-300" fill="#ffffff" stroke-miterlimit="10" stroke-width="0.15px" d="M9.24279,1.60364A3.57028,3.57028,0,0,1,9.03047,3.437a.22517.22517,0,0,1-.13777.127q-.37947.12333-.393-.2577A8.99336,8.99336,0,0,1,8.773,1.28152l.04743-.06627a.09622.09622,0,0,1,.131-.0092A.91174.91174,0,0,1,9.24279,1.60364Z" transform="translate(-0.99243 -0.175)"/>
                  <path fill="#a18974" d="M6.55875,5.56662a.39125.39125,0,0,1-.57982.24849q-.081-.02944.00737-.03313a.42463.42463,0,0,0,.44544-.41783.28789.28789,0,0,1,.39207-.278q.43256.08835.48962-.20983c.011-.05523.0589-.0902.092-.06627q.05154.035-.01473.14173a1.16655,1.16655,0,0,1-.71786.508A.16227.16227,0,0,0,6.55875,5.56662Z" transform="translate(-0.99243 -0.175)"/>
                  <path class="fill-primary-focus" d="M10.20882,7.30238a1.85185,1.85185,0,0,1-1.79467,0q-.10675-.12516-.22272-.24113a1.79085,1.79085,0,0,1-.17118-.24665q-.116-.18407-.32028-.02577a.69827.69827,0,0,1-.15646.092.88472.88472,0,0,0-.162.09387.12911.12911,0,0,0-.046.14726l.243.64791a1.20866,1.20866,0,0,1-.5522,1.38052A1.32166,1.32166,0,0,1,5.3439,8.99581a3.75675,3.75675,0,0,1-.68658-.843.12155.12155,0,0,1,.0405-.16751l5.314-3.07945a.168.168,0,0,1,.23009.06442,3.3594,3.3594,0,0,1,.41231,1.28295A1.08872,1.08872,0,0,1,10.20882,7.30238Z" transform="translate(-0.99243 -0.175)"/>
                  <ellipse class="stroke-base-300" fill="#eae7e6" stroke-miterlimit="10" stroke-width="0.15px" cx="3.24368" cy="5.7908" rx="0.31124" ry="1.01363" transform="translate(-4.30841 6.62858) rotate(-69.52181)"/>
                  <path fill="#c8b399" d="M8.41415,7.30238l-.83567.46753-.243-.64791a.12911.12911,0,0,1,.046-.14726.88472.88472,0,0,1,.162-.09387A.69827.69827,0,0,0,7.7,6.78883q.20431-.15829.32028.02577a1.79085,1.79085,0,0,0,.17118.24665Q8.3074,7.17722,8.41415,7.30238Z" transform="translate(-0.99243 -0.175)"/>
                  <path fill="#eae7e6" d="M8.41415,7.30238a1.85185,1.85185,0,0,0,1.79467,0c.29186,0,.48655.67492.50618.83567A2.08575,2.08575,0,0,1,9.64741,10.4978a1.901,1.901,0,0,1-1.57562.13253,1.67854,1.67854,0,0,1-1.04551-1.4799,1.20866,1.20866,0,0,0,.5522-1.38052Zm.508,1.62532q-.1988-.27057-.38286-.5522a.33494.33494,0,0,1,.02393-.46569c.05338-.05338.081-.11228.0681-.1491q-.03129-.10123-.23376-.07363a.73.73,0,0,0-.37182.162Q7.67053,8.14357,8,8.21536a.38979.38979,0,0,0,.17486-.02393.14377.14377,0,0,1,.18223.0497,6.05085,6.05085,0,0,1,.34421.57613q.22824.43073-.11412.46017-.47675.03866-.07.09756a.16878.16878,0,0,0,.07-.00368,1.09444,1.09444,0,0,0,.74363-.64424q.11412-.26137-.04233-.10676a.16969.16969,0,0,0-.046.08467.41161.41161,0,0,1-.18223.25586A.10481.10481,0,0,1,8.92218,8.9277Z" transform="translate(-0.99243 -0.175)"/>
                  <path fill="#201918" d="M9.06023,8.96084A.41161.41161,0,0,0,9.24246,8.705a.16969.16969,0,0,1,.046-.08467q.15645-.15462.04233.10676a1.09444,1.09444,0,0,1-.74363.64424.16878.16878,0,0,1-.07.00368q-.40678-.0589.07-.09756.34236-.02945.11412-.46017a6.05085,6.05085,0,0,0-.34421-.57613.14377.14377,0,0,0-.18223-.0497A.38979.38979,0,0,1,8,8.21536q-.32947-.07179.02577-.3663a.73.73,0,0,1,.37182-.162q.20247-.0276.23376.07363c.01289.03682-.01472.09572-.0681.1491a.33494.33494,0,0,0-.02393.46569q.18407.28163.38286.5522A.10481.10481,0,0,0,9.06023,8.96084Z" transform="translate(-0.99243 -0.175)"/>
                  <path fill="#a18974" d="M12.50783,9.38419q.27241.74549-.56509.867a.37255.37255,0,0,1-.06443.00184q-.3258-.02393.0405-.09387.72154-.13989.37734-.74916a.13769.13769,0,0,1,.09939-.20431q.93507-.1491.60375-.53012-.06258-.07363.02209-.035a.3181.3181,0,0,1,.19695.37365.20522.20522,0,0,1-.09388.14358.9302.9302,0,0,1-.55772.14909A.05813.05813,0,0,0,12.50783,9.38419Z" transform="translate(-0.99243 -0.175)"/>
                  <path fill="#a18974" d="M9.76705,12.42868q.03313.60742-.48778.3939-.07731-.03129.00737-.02393.29451.02577.324-.243.06258-.56692.51539-.36261a.273.273,0,0,0,.17486.02577q.21352-.05706.20248-.34053-.00921-.21536.06626-.162a.15724.15724,0,0,1,.05154.13805q-.04233.72523-.77309.51171A.06324.06324,0,0,0,9.76705,12.42868Z" transform="translate(-0.99243 -0.175)"/>
                  <path fill="#a18974" d="M13.23858,12.48942a.64732.64732,0,0,0,.24849-.4933q.04049-.381.081,0a.62273.62273,0,0,1-.29451.65528q-.011.00736-.22456.07915-.22457.07362-.15462.335a.22736.22736,0,0,1-.011.16935.59171.59171,0,0,1-.878.219c-.03681-.01841-.0589-.0497-.0497-.07547a.047.047,0,0,1,.02025-.02577.06824.06824,0,0,1,.0589-.0092q.7602.14908.59086-.55957a.12858.12858,0,0,1,.05154-.14173.63658.63658,0,0,1,.28346-.0902A.63958.63958,0,0,0,13.23858,12.48942Z" transform="translate(-0.99243 -0.175)"/>
                </svg>
              </div>
            </div>
            <div
              class="chat-bubble bg-base-100 whitespace-pre-line text-base text-base-content font-light break-words"
            >
              {#if question.data.content === ""}
                <div class="bg-base-200 inline-block rounded py-1 px-4">
                  <div class="dots-load w-2 aspect-square rounded-full"></div>
                </div>
              {/if}
              {question.data.content}
            </div>
          </div>
        {:else if question.type === "system"}
          <div
            class="w-full text-center font-light text-md px-10 md:px-16 py-8"
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
    <div class="flex flex-row justify-between items-center w-full max-w-3xl h-auto bg-base-200 rounded-lg input input-bordered px-0 drop-shadow-md">
      <textarea
        autofocus
        name="question"
        class="flex-1 textarea resize-y bg-[transparent] h-10 text-lg outline-0 ring-0 placeholder-base-content focus:outline-0"
        disabled={isLoading}
        placeholder="Message Serge..."
        bind:value={prompt}
      />
      <button on:mouseenter={onMouseEnter} on:mouseleave={onMouseLeave}
        type="submit"
        disabled={isLoading}
        class="btn btn-[transparent] bg-[transparent] border-0 rounded-l-none rounded-r-lg h-10 w-14 text-lg hover:bg-gradient-to-b hover:from-primary hover:to-primary-focus"
        class:loading={isLoading}
        on:click|preventDefault={askQuestion}
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">
          <path class="{sendBottomHovered ? 'fill-primary-content' : 'fill-base-content'}" d="M.989 8 .064 2.68a1.342 1.342 0 0 1 1.85-1.462l13.402 5.744a1.13 1.13 0 0 1 0 2.076L1.913 14.782a1.343 1.343 0 0 1-1.85-1.463L.99 8Zm.603-5.288L2.38 7.25h4.87a.75.75 0 0 1 0 1.5H2.38l-.788 4.538L13.929 8Z"></path>
        </svg>       
      </button>
    </div>
  </div>
</div>
