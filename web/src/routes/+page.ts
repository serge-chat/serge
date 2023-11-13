import type { PageLoad } from "./$types";

export interface ModelStatus {
  name: string;
  size: number;
  available: boolean;
  progress?: number;
}

export const load: PageLoad = async ({ fetch }) => {
  const api_model = await fetch("/api/model/all");
  const models = (await api_model.json()) as ModelStatus[];
  return {
    models,
  };
};
