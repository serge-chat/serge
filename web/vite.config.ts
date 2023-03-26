import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    proxy: {
      "/api": {
        target: "http://serge:9124/",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/u, ""),
      },
    },
  },
});
