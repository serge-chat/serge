import type { HandleFetch } from "@sveltejs/kit";

export const handleFetch = (({ request, fetch }) => {
  const regex = new RegExp(
    "http://(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]).)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9])/api/"
  );
  request = new Request(
    request.url.replace(regex, "http://api:9124/"),
    request
  );

  return fetch(request);
}) satisfies HandleFetch;
