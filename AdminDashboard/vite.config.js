import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5001', // Change this to your Flask API endpoint
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '') // Remove the '/api' prefix
      }
    }
  }
});
