import type { HandleFetch } from "@sveltejs/kit";

export const handleFetch = (({ request, fetch }) => {
  let parts = request.url.split("?");

  const regex = new RegExp(
    "http://[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*/api/"
  );

  parts[0] = parts[0].replace(regex, "http://api:9124/");

  request = new Request(parts.join("?"), request);

  return fetch(request);
}) satisfies HandleFetch;
