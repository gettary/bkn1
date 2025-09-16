import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // Import the 'path' module

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: ['affiliate-nikon-raw-tomato.trycloudflare.com'], // Allow subdomains of localhost and ngrok-free.app
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src') // Correctly resolve the '@' alias to the 'src' folder
    }
  }
})