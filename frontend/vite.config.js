import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The browser calls /api/... on the Vite dev server and Vite forwards it to the FastAPI backend on port 8000. This avoids needing CORS in development.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // Must remove api before sending to fastapi, otherwise fastapi will not recognize the endpoint.
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
