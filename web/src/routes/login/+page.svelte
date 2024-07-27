<script lang="ts">
  import { goto } from "$app/navigation";
  import { writable } from "svelte/store";

  let username = "";
  let password = "";
  let error = writable<string | null>(null);

  async function handleSubmit(event: Event) {
    event.preventDefault();
    try {
      const response = await fetch("/api/auth/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username,
          password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        goto("/", { invalidateAll: true });
      } else {
        const errorData = await response.json();
        error.set(errorData.detail || "Login failed");
      }
    } catch (err) {
      error.set("An error occurred");
    }
  }
</script>

<main>
  <div class="card-group">
    <div class="card">
      <div class="card-title p-3 text-3xl justify-center font-bold">
        Sign In
      </div>
      <div class="card-body">
        <form on:submit={handleSubmit}>
          <div class="form-control">
            <input
              type="text"
              placeholder="Username"
              bind:value={username}
              required
            />
          </div>
          <div class="form-control">
            <input
              type="password"
              placeholder="Password"
              bind:value={password}
              required
            />
          </div>
          {#if $error}
            <p style="color: red;">{$error}</p>
          {/if}
          <button class="btn" type="submit">Authenticate</button>
        </form>
      </div>
    </div>
  </div>
</main>
