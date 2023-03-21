import type { Actions } from "./$types";

export const actions = {
  default: async ({ fetch, request }) => {
    const formData = await request.formData();

    const convertedFormEntries = Array.from(formData, ([key, value]) => [
      key,
      typeof value === "string" ? value : value.name,
    ]);
    const searchParams = new URLSearchParams(convertedFormEntries);

    const response = await fetch("/api/chat?" + searchParams.toString(), {
      method: "POST",
    });

    if (response.ok) {
      return { success: true };
    } else {
      console.log(response.statusText);
    }
  },
};
