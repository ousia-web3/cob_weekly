import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Listen on all local IPs
    proxy: {
      '/save-json': 'http://localhost:8001',
      '/save-html': 'http://localhost:8001',
      '/send-email': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        timeout: 120000, // 2분 타임아웃
      },
      '/api': 'http://localhost:8001',
      '/recipients': 'http://localhost:8001',
      '/uploads': 'http://localhost:8001', // If there are any file serving endpoints
    },
  },
})
