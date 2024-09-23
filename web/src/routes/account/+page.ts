import type { Load } from "@sveltejs/kit";

interface User {
  id: string;
  username: string;
  email: string;
  pref_theme: "light" | "dark";
  full_name: string;
  default_prompt: string;
}

export const load: Load = async () => {
  const user = await fetch("/api/user/", {
    method: "GET",
  })
    .then((response) => {
      if (response.status == 401) {
        window.location.href = "/";
      }
      return response.json();
    })
    .catch((error) => {
      console.log(error);
      window.location.href = "/";
    });
  return { user };
};
