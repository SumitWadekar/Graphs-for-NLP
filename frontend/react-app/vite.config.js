import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/build-graph-from-text': 'http://127.0.0.1:8000',
      '/upload-contract-csv': 'http://127.0.0.1:8000',
      '/build-graph-from-clauses': 'http://127.0.0.1:8000',
      '/api-info': 'http://127.0.0.1:8000'
    }
  }
})
