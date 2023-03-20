import type { LayoutLoad } from "./$types";

type t = {
  id: string;
  created: string;
  model: string;
};

export const load: LayoutLoad = async ({ fetch }) => {
  const r = await fetch("http://api:9124/chats");
  const chats = (await r.json()) as t[];
  return {
    chats: chats,
  };
};
