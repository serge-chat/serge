<script context="module" lang="ts">
  export { load } from "./+page";
</script>

<script lang="ts">
  import { writable } from "svelte/store";
  import { goto } from "$app/navigation";
  export let data: {
    user: {
      username: string;
      email: string;
      full_name: string;
      pref_theme: "light" | "dark";
      default_prompt: string;
    } | null;
  };
  let user = data.user;
  let username: string = user?.username ?? "";
  let email: string = user?.email ?? "";
  let full_name: string = user?.full_name ?? "";
  let pref_theme: "light" | "dark" = user?.pref_theme ?? "light";
  let default_prompt: string = user?.default_prompt ?? "";
  let status = writable<string | null>(null);

  async function handleSubmit(event: Event) {
    event.preventDefault();
    // Implement the update logic here, e.g., sending a PUT request to update user preferences
    try {
      await fetch("/api/user/", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          email,
          full_name,
          pref_theme,
          default_prompt,
        }),
      });

      status.set("Preferences updated successfully");
      goto("/", { invalidateAll: true });
    } catch (error) {
      if (error instanceof Error) {
        status.set(error.message);
      } else {
        status.set("Failed to update preferences");
      }
    }
  }
</script>

<main>
  <div class="card-group">
    <div class="card">
      <div class="card-title p-3 text-3xl justify-center font-bold">
        User Preferences
      </div>
      <div class="card-body">
        {#if user}
          <form on:submit={handleSubmit}>
            <div class="input-group">
              <div class="input-group-prepend">
                <span class="input-group-text">Username</span>
              </div>
              <input type="text" bind:value={username} disabled />
            </div>
            <div class="input-group">
              <div class="input-group-prepend">
                <span class="input-group-text">Full Name</span>
              </div>
              <input id="full_name" type="text" bind:value={full_name} />
            </div>
            <div class="input-group">
              <div class="input-group-prepend">
                <span class="input-group-text">Email</span>
              </div>
              <input id="email" type="email" bind:value={email} />
            </div>
            <div class="input-group">
              <div class="input-group-prepend">
                <span class="input-group-text">Default Prompt</span>
              </div>
              <textarea
                id="default_prompt"
                bind:value={default_prompt}
                style="resize:both; width:100%;"
              />
            </div>
            {#if $status}
              <p>{$status}</p>
            {/if}
            <button class="btn" type="submit">Save Preferences</button>
          </form>
        {:else}
          <p>Loading...</p>
        {/if}
      </div>
    </div>
  </div>
</main>
