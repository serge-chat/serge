import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
  const r = await fetch("api/models");
  const models = (await r.json()) as string[];
  return {
    models,
  };
};
