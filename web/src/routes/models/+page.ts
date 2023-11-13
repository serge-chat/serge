import type { PageLoad } from "./$types";

interface ModelStatus {
  name: string;
  size: number;
  available: boolean;
  progress: number;
}

export const load: PageLoad = async ({ fetch }) => {
  const r = await fetch("/api/model/all");
  const models = (await r.json()) as ModelStatus[];
  return {
    models,
  };
};
