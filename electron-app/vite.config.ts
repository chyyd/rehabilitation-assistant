import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    electron([
      {
        // 主进程入口
        entry: 'electron/main.ts',
        vite: {
          build: {
            rollupOptions: {
              external: ['electron']
            }
          }
        }
      },
      {
        // Preload脚本入口
        entry: 'preload/index.ts',
        onstart(args) {
          console.log('Preload script starting...')
        },
        vite: {
          build: {
            rollupOptions: {
              external: ['electron']
            }
          }
        }
      }
    ]),
    renderer()
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173
  },
  // 优化preload输出路径
  build: {
    rollupOptions: {
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  }
})
