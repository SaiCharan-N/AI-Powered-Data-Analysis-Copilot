import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    esbuildOptions: {
      target: "esnext",
    },
  },
  build: {
    chunkSizeWarningLimit: 700,
    target: "esnext",
    rollupOptions: {
      output: {
        manualChunks: {
          charts: ["recharts"],
          vendor: ["react", "react-dom", "axios", "lucide-react"],
        },
      },
    },
  },
  server: {
    port: 5173,
    strictPort: false,
  },
});
