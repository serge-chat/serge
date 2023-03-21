import type { HandleFetch } from "@sveltejs/kit";

export const handleFetch = (({ request, fetch }) => {
  request = new Request(
    request.url.replace("http://localhost/api/", "http://api:9124/"),
    request
  );

  return fetch(request);
}) satisfies HandleFetch;
