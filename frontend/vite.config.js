import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  publicDir: 'public',
  build: {
    rollupOptions: {
      input: {
        login: resolve(__dirname, 'src/login/index.html'),
        privacy: resolve(__dirname, 'src/privacy/index.html'),
      },
    },
  },
})
