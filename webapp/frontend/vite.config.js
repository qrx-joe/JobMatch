import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/upload-and-filter': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/cities': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/qualifications': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
