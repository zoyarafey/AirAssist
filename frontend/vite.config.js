import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// FIX 1: Proxy all /api/* requests to backend
// This means frontend uses /api/login, /api/signup etc (no hardcoded port)
// Vite forwards them to http://localhost:8000/login, /signup etc (strips /api prefix)
// This eliminates CORS issues entirely because browser only talks to port 3000
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
