import type { PageLoad } from "./$types";

type MessageType = "human" | "ai" | "system";

type MessageData = {
  content: string;
  additional_kwargs?: Record<string, string>;
};

type Message = {
  type: MessageType;
  data: MessageData;
};

type Params = {
  model_path: string;
  n_ctx: number;
  n_threads: number;
  last_n_tokens_size: number;
  max_tokens: number;
  temperature: number;
  top_p: number;
  repeat_penalty: number;
  top_k: number;
};

type Response = {
  id: string;
  created: string;
  params: Params;
  history: Message[];
};

export const load: PageLoad = async ({ fetch, params }) => {
  const r = await fetch("/api/chat/" + params.id);
  const data = (await r.json()) as Response;

  return {
    chat: data,
  };
};
