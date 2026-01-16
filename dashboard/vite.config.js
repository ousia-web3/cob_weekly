import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Listen on all local IPs
    proxy: {
      '/analyze': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        timeout: 300000, // 5분 타임아웃
        proxyTimeout: 300000,
      },
      '/save-json': 'http://localhost:8001',
      '/save-html': 'http://localhost:8001',
      '/uploads': 'http://localhost:8001', // If there are any file serving endpoints
    },
  },
})
