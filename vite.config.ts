import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import axios from 'axios'

const request = axios.create({
  baseURL: 'http://192.168.1.20:5173/api'
})

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  css: {
    preprocessorOptions: {
      css: {
        charset: false
      }
    }
  },
  server: {
    host: '0.0.0.0',  // 允许局域网访问
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://192.168.1.20:5000',  // 使用你的内网IP
        changeOrigin: true
      }
    }
  },
  base: '/'
})  