import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Forward API calls to the FastAPI backend during development so the
    // browser can use same-origin `/api/...` requests (no CORS needed in dev).
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
