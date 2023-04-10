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
  max_tokens: number;
  temperature: number;
  top_p: number;
  logprobs?: boolean;
  echo: boolean;
  stop_sequences: string[];
  repeat_penalty: number;
  top_k: number;
  n_threads: number;
  n_ctx: number;
  n_parts: number;
  seed: number;
  f16_kv: boolean;
  logits_all: boolean;
  vocab_only: boolean;
  use_mlock: boolean;
  n_batch: number;
  last_n_tokens_size: number;
  streaming: boolean;
  _type: string;
};

type Response = {
  id: string;
  created: string;
  llm: Params;
  history: Message[];
};

export const load: PageLoad = async ({ fetch, params }) => {
  const r = await fetch("/api/chat/" + params.id);
  const data = (await r.json()) as Response;

  return {
    chat: data,
  };
};
