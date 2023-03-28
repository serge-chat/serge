import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
  const r = await fetch("/api/model/");
  const models = (await r.json()) as string[];
  return {
    models,
  };
};
