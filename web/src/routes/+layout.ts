import type { LayoutLoad } from "./$types";

interface ChatMetadata {
  id: string;
  created: string;
  model: string;
  subtitle: string;
}

export interface ModelStatus {
  name: string;
  size: number;
  available: boolean;
  progress?: number;
}

export const load: LayoutLoad = async ({ fetch }) => {
  const api_chat = await fetch("/api/chat/");
  const chats = (await api_chat.json()) as ChatMetadata[];

  const model_api = await fetch("/api/model/all");
  const models = (await model_api.json()) as ModelStatus[];
  return {
    chats,
    models,
  };
};
