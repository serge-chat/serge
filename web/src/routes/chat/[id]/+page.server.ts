import type { Actions } from "./$types";

export const actions = {
  default: async ({ fetch, params, request }) => {
    const data = await request.formData();
    const question = data.get("question");

    if (question) {
      let data = new URLSearchParams();
      data.append("prompt", question.toString());

      const response = await fetch(
        "http://api:9124/chat/" + params.id + "/question?" + data.toString(),
        {
          method: "POST",
        }
      );

      if (response.ok) {
        return { success: true };
      } else {
        console.log(response.statusText);
      }
    }
  },
};
