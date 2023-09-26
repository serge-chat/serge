import type { PageLoad } from "./$types";

type MessageType = "human" | "ai" | "system";

interface MessageData {
  content: string;
}

interface Message {
  type: MessageType;
  data: MessageData;
}

interface Params {
  model_path: string;
  n_ctx: number;
  n_gpu_layers: number;
  n_threads: number;
  last_n_tokens_size: number;
  max_tokens: number;
  temperature: number;
  top_p: number;
  repeat_penalty: number;
  top_k: number;
}

interface Response {
  id: string;
  created: string;
  params: Params;
  history: Message[];
}

export const load: PageLoad = async ({ fetch, params }) => {
  const r = await fetch("/api/chat/" + params.id);
  const data = (await r.json()) as Response;

  return {
    chat: data,
  };
};
