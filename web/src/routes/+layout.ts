import type { LayoutLoad } from "./$types";

interface ChatMetadata {
  id: string;
  created: string;
  model: string;
  subtitle: string;
}

export const ssr = false; // off for now because ssr with auth is broken

export interface ModelStatus {
  name: string;
  size: number;
  available: boolean;
  progress?: number;
}

export interface User {
  username: string;
  email: string;
  pref_theme: "light" | "dark";
  full_name: string;
  default_prompt: string;
}

export const load: LayoutLoad = async ({ fetch }) => {
  let userData: User | null = null;

  const api_chat = await fetch("/api/chat/");
  const chats = (await api_chat.json()) as ChatMetadata[];

  const model_api = await fetch("/api/model/all");
  const models = (await model_api.json()) as ModelStatus[];

  const userData_api = await fetch("/api/user/");
  if (userData_api.ok) {
    userData = (await userData_api.json()) as User;
  }

  return {
    chats,
    models,
    userData,
  };
};
