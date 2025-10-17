import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from "@tailwindcss/vite"
import path from "path"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
      }

    },
    allowedHosts: ['demo.dev.xyz', 'netflix.demo.dev.xyz', 'fsrapp.netflix.com', 'localhost']
  },
  build: {
    outDir: "../../backend/api/ui",
    emptyOutDir: true,
  },
})
