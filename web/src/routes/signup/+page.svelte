<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  let username = "";
  let secret = "";
  let full_name = "";
  let email = "";
  let auth_type = 1;
  let error = "";
  let success = "";

  async function handleSubmit(event: Event) {
    event.preventDefault();
    error = "";
    success = "";
    const response = await fetch("/api/user/create", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        secret,
        full_name,
        email,
        auth_type,
      }),
    });

    if (response.ok) {
      success = "User created successfully!";
      await authAfterCreate(event)
      goto("/account");
    } else {
      const data = await response.json();
      error = data.detail || "An error occurred";
    }
  }

  async function authAfterCreate(event: Event) {
    event.preventDefault();
    try {
      const response = await fetch("/api/auth/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          "username": username,
          "password": secret,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        goto("/");
      } else {
        const errorData = await response.json();
        error = errorData.detail || "Login failed";
      }
    } catch (err) {
      error = "An error occurred";
    }
  }
</script>

<main>
  <div class="card-group">
    <div class="card">
      <div class="card-title p-3 text-3xl justify-center font-bold">Register a new user</div>
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
              bind:value={secret}
              required
            />
          </div>

          {#if error}
            <p class="error-message">{error}</p>
          {/if}
          {#if success}
            <p class="success-message">{success}</p>
          {/if}
          <button class="btn" type="submit">Submit</button>
        </form>
      </div>
    </div>
    <div class="card">
      <div class="card-title p-3 text-3xl justify-center font-bold">
        Or link an account (comming soon)
      </div>
      <div class="card-body">
        <button name="google-btn" class="btn" disabled={true}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="currentColor"
            viewBox="0 0 16 16"
          >
            <path
              d="M15.545 6.558a9.4 9.4 0 0 1 .139 1.626c0 2.434-.87 4.492-2.384 5.885h.002C11.978 15.292 10.158 16 8 16A8 8 0 1 1 8 0a7.7 7.7 0 0 1 5.352 2.082l-2.284 2.284A4.35 4.35 0 0 0 8 3.166c-2.087 0-3.86 1.408-4.492 3.304a4.8 4.8 0 0 0 0 3.063h.003c.635 1.893 2.405 3.301 4.492 3.301 1.078 0 2.004-.276 2.722-.764h-.003a3.7 3.7 0 0 0 1.599-2.431H8v-3.08z"
            />
          </svg>
          <span>Link Google Account</span>
        </button>
        <button name="reddit-btn" class="btn" disabled={true}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="currentColor"
            viewBox="0 0 16 16"
          >
            <path
              d="M6.167 8a.83.83 0 0 0-.83.83c0 .459.372.84.83.831a.831.831 0 0 0 0-1.661m1.843 3.647c.315 0 1.403-.038 1.976-.611a.23.23 0 0 0 0-.306.213.213 0 0 0-.306 0c-.353.363-1.126.487-1.67.487-.545 0-1.308-.124-1.671-.487a.213.213 0 0 0-.306 0 .213.213 0 0 0 0 .306c.564.563 1.652.61 1.977.61zm.992-2.807c0 .458.373.83.831.83s.83-.381.83-.83a.831.831 0 0 0-1.66 0z"
            />
            <path
              d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.828-1.165c-.315 0-.602.124-.812.325-.801-.573-1.9-.945-3.121-.993l.534-2.501 1.738.372a.83.83 0 1 0 .83-.869.83.83 0 0 0-.744.468l-1.938-.41a.2.2 0 0 0-.153.028.2.2 0 0 0-.086.134l-.592 2.788c-1.24.038-2.358.41-3.17.992-.21-.2-.496-.324-.81-.324a1.163 1.163 0 0 0-.478 2.224q-.03.17-.029.353c0 1.795 2.091 3.256 4.669 3.256s4.668-1.451 4.668-3.256c0-.114-.01-.238-.029-.353.401-.181.688-.592.688-1.069 0-.65-.525-1.165-1.165-1.165"
            />
          </svg>
          <span>Link Reddit Account</span>
        </button>
      </div>
    </div>
    <div class="card">
      <div class="card-title pt-3 text-3xl justify-center font-bold">
        Already have an account?
      </div>
      <div class="card-body">
        <button
          name="login-btn"
          class="btn"
          on:click={() => goto("/login")}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="currentColor"
            class="mr-3"
            viewBox="0 0 16 16"
          >
          <path d="M12.5 16a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7m1.679-4.493-1.335 2.226a.75.75 0 0 1-1.174.144l-.774-.773a.5.5 0 0 1 .708-.708l.547.548 1.17-1.951a.5.5 0 1 1 .858.514M11 5a3 3 0 1 1-6 0 3 3 0 0 1 6 0M8 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4"/>
          <path d="M8.256 14a4.5 4.5 0 0 1-.229-1.004H3c.001-.246.154-.986.832-1.664C4.484 10.68 5.711 10 8 10q.39 0 .74.025c.226-.341.496-.65.804-.918Q8.844 9.002 8 9c-5 0-6 3-6 4s1 1 1 1z"/>        
          </svg>
          <span>Login Instead</span>
        </button>
      </div>
    </div>
  </div>
</main>
