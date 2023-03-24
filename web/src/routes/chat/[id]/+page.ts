import type { PageLoad } from "./$types";

type question = {
  _id: string;
  question: string;
  answer?: string;
  error?: string;
};

type params = {
  _id: string;
  model: string;
  temperature: number;
  top_k: number;
  top_p: number;
  max_length: number;
  repeat_last_n: number;
  repeat_penalty: number;
};

type t = {
  _id: string;
  created: string;
  parameters: params;
  questions: question[] | null;
};

export const load: PageLoad = async ({ fetch, params }) => {
  const r = await fetch("/api/chat/" + params.id);
  const data = (await r.json()) as t;
  return {
    props: data,
  };
};
