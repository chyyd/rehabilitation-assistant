import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// 纯 Web 模式配置（不包含 Electron）
// 用于浏览器独立访问 http://localhost:5173/
export default defineConfig({
  plugins: [
    vue()
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: true // 允许外部访问
  }
})
