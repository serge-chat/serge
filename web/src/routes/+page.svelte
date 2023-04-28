<script lang="ts">
  import type { PageData } from "./$types";
  import { goto, invalidate } from "$app/navigation";
  export let data: PageData;

  const models = data.models.filter((el) => el.available);

  const modelAvailable = models.length > 0;
  const modelsLabels = models.map((el) => el.name);

  let temp = 0.1;
  let top_k = 50;
  let top_p = 0.95;

  let max_length = 256;
  let repeat_last_n = 64;
  let repeat_penalty = 1.3;

  let init_prompt =
    "Below is an instruction that describes a task. Write a response that appropriately completes the request.";

  let n_threads = 4;
  let context_window = 512;

  async function onCreateChat(event: Event) {
    const form = document.getElementById("form-create-chat") as HTMLFormElement;

    const formData = new FormData(form);

    const convertedFormEntries = Array.from(formData, ([key, value]) => [
      key,
      typeof value === "string" ? value : value.name,
    ]);
    const searchParams = new URLSearchParams(convertedFormEntries);

    const r = await fetch("/api/chat/?" + searchParams.toString(), {
      method: "POST",
    });

    if (r.ok) {
      const data = await r.json();
      await goto("/chat/" + data);
      await invalidate("/api/chat/");
    }
  }
</script>

<div class="pt-5 flex flex-col justify-center items-center">
  <h1 class="pb-2 text-3xl font-bold">Say Hi to Serge</h1>
  <div class="w-[2.6rem] bg-gradient-to-b from-primary to-primary-focus mask mask-squircle online">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="48" height="48">
      <path class="stroke-base-100" fill="#c8b399" stroke-miterlimit="10" stroke-width="0.15px" d="M14.71526,15.15914q.15645-3.39789.2172-6.79948a.25392.25392,0,0,0-.0589-.16013L14.406,7.5921a.30419.30419,0,0,0-.34422-.11044q-.63133.2448-.74732-.02393a1.95718,1.95718,0,0,1-.14725-.554q-.10122-.87433-.64239-.74364a1.99586,1.99586,0,0,1-.54116.09019q-.52092-.10492-.4344-.80622.07916-.6387-.716-.762a.47745.47745,0,0,1-.4344-.43441,1.89641,1.89641,0,0,0-.416-.82278c-.11611-.15881-.23745-.05338-.23745-.05338q-.26872.37366-.27794.01105a.71088.71088,0,0,1,.02577-.18776A6.2486,6.2486,0,0,0,9.61842.61776a.67718.67718,0,0,0-1.19645,0,4.54511,4.54511,0,0,0-.66265,2.19777q-.0055.10492-.05153.01289a.56.56,0,0,1-.05339-.2669.10787.10787,0,0,0-.08282-.11412.849.849,0,0,0-.762.20984.34138.34138,0,0,0-.0902.15461.41776.41776,0,0,1-.66449.28715.23265.23265,0,0,0-.17118-.02025q-.26505.09572-.27058.5522-.00183.3663-.36262.29819-.66263-.127-.56876.497a.11856.11856,0,0,1-.09756.13621q-.94057.16382-.208.74.32766.25767-.04969.07914a10.54646,10.54646,0,0,0-1.55169-.58166,2.35641,2.35641,0,0,0-1.27192-.01472q-.68472.18039-.29266.78229a2.49922,2.49922,0,0,0,2.518,1.18356q.25953-.02577.138.081a.20376.20376,0,0,1-.13069.03129q-.12333-.00368-.1675.13989a5.33888,5.33888,0,0,0-.17855.74732.7172.7172,0,0,0,.34973.83566q.39023.20985.39207.21169a.71407.71407,0,0,1,.18407.70314.37974.37974,0,0,0,.36445.50986,1.17377,1.17377,0,0,1,.62766.2982.219.219,0,0,1,.06628.15645q.02208.61664.67921.532a.1806.1806,0,0,1,.15645.05153,1.402,1.402,0,0,1,.32948.62768.11491.11491,0,0,0,.11229.08467.62276.62276,0,0,1,.69026.53748.92728.92728,0,0,0,.15092.41231.59356.59356,0,0,0,.43625.19143.40358.40358,0,0,1,.43624.41231.71483.71483,0,0,0,.82831.74.73873.73873,0,0,1,.58718.29819.15558.15558,0,0,0,.14541.0497.638.638,0,0,1,.76572.31659.18671.18671,0,0,0,.18223.09941,1.26348,1.26348,0,0,1,1.11545.31475.13072.13072,0,0,0,.14173.03681.89878.89878,0,0,1,1.0087.18407.55982.55982,0,0,0,.79333.081q.3037-.22641.41416.13069l.41415.18407A5.85415,5.85415,0,0,1,14.71526,15.15914Z" transform="translate(-0.99243 -0.175)"/>
      <path class="stroke-base-100" fill="#ffffff" stroke-miterlimit="10" stroke-width="0.15px" d="M9.24279,1.60364A3.57028,3.57028,0,0,1,9.03047,3.437a.22517.22517,0,0,1-.13777.127q-.37947.12333-.393-.2577A8.99336,8.99336,0,0,1,8.773,1.28152l.04743-.06627a.09622.09622,0,0,1,.131-.0092A.91174.91174,0,0,1,9.24279,1.60364Z" transform="translate(-0.99243 -0.175)"/>
      <path fill="#a18974" d="M6.55875,5.56662a.39125.39125,0,0,1-.57982.24849q-.081-.02944.00737-.03313a.42463.42463,0,0,0,.44544-.41783.28789.28789,0,0,1,.39207-.278q.43256.08835.48962-.20983c.011-.05523.0589-.0902.092-.06627q.05154.035-.01473.14173a1.16655,1.16655,0,0,1-.71786.508A.16227.16227,0,0,0,6.55875,5.56662Z" transform="translate(-0.99243 -0.175)"/>
      <path class="fill-primary-focus" d="M10.20882,7.30238a1.85185,1.85185,0,0,1-1.79467,0q-.10675-.12516-.22272-.24113a1.79085,1.79085,0,0,1-.17118-.24665q-.116-.18407-.32028-.02577a.69827.69827,0,0,1-.15646.092.88472.88472,0,0,0-.162.09387.12911.12911,0,0,0-.046.14726l.243.64791a1.20866,1.20866,0,0,1-.5522,1.38052A1.32166,1.32166,0,0,1,5.3439,8.99581a3.75675,3.75675,0,0,1-.68658-.843.12155.12155,0,0,1,.0405-.16751l5.314-3.07945a.168.168,0,0,1,.23009.06442,3.3594,3.3594,0,0,1,.41231,1.28295A1.08872,1.08872,0,0,1,10.20882,7.30238Z" transform="translate(-0.99243 -0.175)"/>
      <ellipse class="stroke-base-100" fill="#eae7e6" stroke-miterlimit="10" stroke-width="0.15px" cx="3.24368" cy="5.7908" rx="0.31124" ry="1.01363" transform="translate(-4.30841 6.62858) rotate(-69.52181)"/>
      <path fill="#c8b399" d="M8.41415,7.30238l-.83567.46753-.243-.64791a.12911.12911,0,0,1,.046-.14726.88472.88472,0,0,1,.162-.09387A.69827.69827,0,0,0,7.7,6.78883q.20431-.15829.32028.02577a1.79085,1.79085,0,0,0,.17118.24665Q8.3074,7.17722,8.41415,7.30238Z" transform="translate(-0.99243 -0.175)"/>
      <path fill="#eae7e6" d="M8.41415,7.30238a1.85185,1.85185,0,0,0,1.79467,0c.29186,0,.48655.67492.50618.83567A2.08575,2.08575,0,0,1,9.64741,10.4978a1.901,1.901,0,0,1-1.57562.13253,1.67854,1.67854,0,0,1-1.04551-1.4799,1.20866,1.20866,0,0,0,.5522-1.38052Zm.508,1.62532q-.1988-.27057-.38286-.5522a.33494.33494,0,0,1,.02393-.46569c.05338-.05338.081-.11228.0681-.1491q-.03129-.10123-.23376-.07363a.73.73,0,0,0-.37182.162Q7.67053,8.14357,8,8.21536a.38979.38979,0,0,0,.17486-.02393.14377.14377,0,0,1,.18223.0497,6.05085,6.05085,0,0,1,.34421.57613q.22824.43073-.11412.46017-.47675.03866-.07.09756a.16878.16878,0,0,0,.07-.00368,1.09444,1.09444,0,0,0,.74363-.64424q.11412-.26137-.04233-.10676a.16969.16969,0,0,0-.046.08467.41161.41161,0,0,1-.18223.25586A.10481.10481,0,0,1,8.92218,8.9277Z" transform="translate(-0.99243 -0.175)"/>
      <path fill="#201918" d="M9.06023,8.96084A.41161.41161,0,0,0,9.24246,8.705a.16969.16969,0,0,1,.046-.08467q.15645-.15462.04233.10676a1.09444,1.09444,0,0,1-.74363.64424.16878.16878,0,0,1-.07.00368q-.40678-.0589.07-.09756.34236-.02945.11412-.46017a6.05085,6.05085,0,0,0-.34421-.57613.14377.14377,0,0,0-.18223-.0497A.38979.38979,0,0,1,8,8.21536q-.32947-.07179.02577-.3663a.73.73,0,0,1,.37182-.162q.20247-.0276.23376.07363c.01289.03682-.01472.09572-.0681.1491a.33494.33494,0,0,0-.02393.46569q.18407.28163.38286.5522A.10481.10481,0,0,0,9.06023,8.96084Z" transform="translate(-0.99243 -0.175)"/>
      <path fill="#a18974" d="M12.50783,9.38419q.27241.74549-.56509.867a.37255.37255,0,0,1-.06443.00184q-.3258-.02393.0405-.09387.72154-.13989.37734-.74916a.13769.13769,0,0,1,.09939-.20431q.93507-.1491.60375-.53012-.06258-.07363.02209-.035a.3181.3181,0,0,1,.19695.37365.20522.20522,0,0,1-.09388.14358.9302.9302,0,0,1-.55772.14909A.05813.05813,0,0,0,12.50783,9.38419Z" transform="translate(-0.99243 -0.175)"/>
      <path fill="#a18974" d="M9.76705,12.42868q.03313.60742-.48778.3939-.07731-.03129.00737-.02393.29451.02577.324-.243.06258-.56692.51539-.36261a.273.273,0,0,0,.17486.02577q.21352-.05706.20248-.34053-.00921-.21536.06626-.162a.15724.15724,0,0,1,.05154.13805q-.04233.72523-.77309.51171A.06324.06324,0,0,0,9.76705,12.42868Z" transform="translate(-0.99243 -0.175)"/>
      <path fill="#a18974" d="M13.23858,12.48942a.64732.64732,0,0,0,.24849-.4933q.04049-.381.081,0a.62273.62273,0,0,1-.29451.65528q-.011.00736-.22456.07915-.22457.07362-.15462.335a.22736.22736,0,0,1-.011.16935.59171.59171,0,0,1-.878.219c-.03681-.01841-.0589-.0497-.0497-.07547a.047.047,0,0,1,.02025-.02577.06824.06824,0,0,1,.0589-.0092q.7602.14908.59086-.55957a.12858.12858,0,0,1,.05154-.14173.63658.63658,0,0,1,.28346-.0902A.63958.63958,0,0,0,13.23858,12.48942Z" transform="translate(-0.99243 -0.175)"/>
    </svg>
  </div>
</div>
<h1 class="text-xl font-light text-center pt-2 pb-5">
  An easy way to chat with Alpaca & other LLaMA based models.
</h1>

<form on:submit|preventDefault={onCreateChat} id="form-create-chat" class="p-5">
  <div class="w-full pb-20">
    <div class="mx-auto w-fit pt-5">
      <button
        type="submit"
        class="btn btn-primary mx-5"
        disabled={!modelAvailable}>Start a new chat</button
      >
      <button
        on:click={() => goto("/models")}
        type="button"
        class="btn btn-outline mx-5">Download Models</button
      >
    </div>
  </div>

  <div tabindex="-1" class="collapse collapse-arrow rounded-box bg-base-200">
    <input type="checkbox" />
    <div class="collapse-title text-xl font-medium">Model settings</div>
    <div class="collapse-content">
      <div class="grid grid-cols-3 gap-4 p-3">
        <div
          class="tooltip tooltip-bottom col-span-2"
          data-tip="The higher the temperature, the more random the model output."
        >
          <label for="temperature" class="label-text"
            >Temperature - [{temp}]</label
          >
          <input
            name="temperature"
            type="range"
            bind:value={temp}
            min="0.05"
            max="2"
            step="0.05"
            class="range range-sm mt-auto"
          />
        </div>
        <div
          class="flex flex-col tooltip tooltip-bottom"
          data-tip="The number of samples to consider for top_k sampling. "
        >
          <label for="top_k" class="label-text pb-1">top_k</label>
          <input
            class="input input-bordered w-full max-w-xs"
            name="top_k"
            type="number"
            bind:value={top_k}
            min="0"
            max="100"
          />
        </div>
        <div class="col-span-2">
          <label for="max_length" class="label-text"
            >Maximum generated text length in tokens - [{max_length}]</label
          >
          <input
            name="max_length"
            type="range"
            bind:value={max_length}
            min="16"
            max="512"
            step="16"
            class="range range-sm mt-auto"
          />
        </div>
        <div
          class="flex flex-col tooltip"
          data-tip="The cumulative probability of the tokens to keep for nucleus sampling. "
        >
          <label for="top_p" class="label-text pb-1">top_p</label>
          <input
            class="input input-bordered w-full max-w-xs"
            name="top_p"
            type="number"
            bind:value={top_p}
            min="0"
            max="1"
            step="0.025"
          />
        </div>
        <div
          class="tooltip col-span-2"
          data-tip="Size of the prompt context. Will determine how far the model will read back. Increases memory consumption."
        >
          <label for="context_window" class="label-text"
            >Prompt Context Length - [{context_window}]</label
          >
          <input
            name="context_window"
            type="range"
            bind:value={context_window}
            min="16"
            max="2048"
            step="16"
            class="range range-sm mt-auto"
          />
        </div>

        <div
          class="flex flex-col tooltip"
          data-tip="Number of tokens to look back on for deciding to apply the repeat penalty."
        >
          <label for="repeat_last_n" class="label-text pb-1"
            >repeat_last_n</label
          >
          <input
            class="input input-bordered w-full max-w-xs"
            name="repeat_last_n"
            type="number"
            bind:value={repeat_last_n}
            min="0"
            max="100"
          />
        </div>
        <div class="flex flex-col">
          <label for="model" class="label-text pb-1"> Model choice </label>
          <select name="model" class="select select-bordered w-full max-w-xs">
            {#each modelsLabels as model}
              <option value={model}>{model}</option>
            {/each}
          </select>
        </div>
        <div
          class="flex flex-col tooltip"
          data-tip="Number of threads to run LLaMA on."
        >
          <label for="n_threads" class="label-text pb-1">n_threads</label>
          <input
            class="input input-bordered w-full max-w-xs"
            name="n_threads"
            type="number"
            bind:value={n_threads}
            min="0"
            max="64"
          />
        </div>
        <div
          class="flex flex-col tooltip"
          data-tip="The weight of the penalty to avoid repeating the last repeat_last_n tokens. "
        >
          <label for="repeat_penalty" class="label-text pb-1">
            repeat_penalty
          </label>
          <input
            class="input input-bordered w-full max-w-xs"
            name="repeat_penalty"
            type="number"
            bind:value={repeat_penalty}
            min="0"
            max="2"
            step="0.05"
          />
        </div>
        <div class="col-span-3 flex flex-col">
          <label for="init_prompt" class="label-text pb-1"
            >Pre-Prompt for initializing a conversation.</label
          >
          <textarea
            class="textarea h-24 textarea-bordered w-full"
            name="init_prompt"
            bind:value={init_prompt}
            placeholder="Enter your prompt here"
          />
        </div>
      </div>
    </div>
  </div>
</form>
