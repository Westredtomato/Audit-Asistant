/*import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
})*/
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    // 开发环境API代理配置
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path  // 保持路径不变
      },
      '/auth': {
        target: 'http://127.0.0.1:8000/api/v1',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth/, '/auth')
      }
    }
  }
})