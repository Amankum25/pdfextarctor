import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/upload': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ask': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/status': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
