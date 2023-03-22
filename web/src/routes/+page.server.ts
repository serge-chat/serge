import { redirect } from "@sveltejs/kit";
import type { Actions } from "./$types";

export const actions = {
  default: async ({ fetch, request }) => {
    const formData = await request.formData();

    const convertedFormEntries = Array.from(formData, ([key, value]) => [
      key,
      typeof value === "string" ? value : value.name,
    ]);
    const searchParams = new URLSearchParams(convertedFormEntries);

    const r = await fetch("/api/chat?" + searchParams.toString(), {
      method: "POST",
    });
    if (r.ok) {
      const data = await r.json();
      throw redirect(303, "/chat/" + data);
    } else {
      console.log(r.statusText);
    }
  },
} satisfies Actions;
