import type { LayoutLoad } from "./$types";

type t = {
  id: string;
  created: string;
  model: string;
  subtitle: string;
};

export const load: LayoutLoad = async ({ fetch }) => {
  const r = await fetch("/api/chats");
  const chats = (await r.json()) as t[];
  return {
    chats: chats,
  };
};
