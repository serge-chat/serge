import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ fetch }) => {
  const r = await fetch("http://api:9124/chats");
  const chats = (await r.json()) as string[];
  return {
    chats: chats,
  };
};
