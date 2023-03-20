import type { Actions } from "./$types";

export const actions = {
  default: async ({ fetch, request }) => {
    const formData = await request.formData();
    const model = formData.get("model");

    let data = new URLSearchParams();
    if (model) {
      data.append("model", model.toString());
    }

    const response = await fetch("http://api:9124/chat?" + data.toString(), {
      method: "POST",
    });

    if (response.ok) {
      return { success: true };
    } else {
      console.log(response.statusText);
    }
  },
};
