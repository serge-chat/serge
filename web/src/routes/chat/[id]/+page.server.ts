import type { PageServerLoad } from "./$types";
import Redis from "ioredis";

const redis = new Redis({
  host: "127.0.0.1",
  port: 6379,
});

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
  owner: string;
  history: Message[];
}

export const load: PageServerLoad = async ({ params }) => {
  const chatId = params.id;

  // Fetch data from Redis
  let chatData;
  try {
    chatData = ((await redis.get(`chat:${chatId}`)) ?? {}) as Response;
  } catch (error) {
    console.error("Failed to fetch chat data from Redis:", error);
    chatData = null;
  }

  return {
    chat: chatData,
  };
};
