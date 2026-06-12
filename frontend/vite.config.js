import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, proxy the API so the frontend can use relative URLs (no CORS friction).
// In production the FastAPI server serves this build at "/" on the same origin.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/review": { target: "http://localhost:8000", changeOrigin: true },
      "/health": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
