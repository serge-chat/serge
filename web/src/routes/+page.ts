import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
  const r = await fetch("http://api:9124/models");
  const models = (await r.json()) as string[];
  return {
    models,
  };
};
