import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const devProxyCookie = env.VITE_DEV_PROXY_COOKIE

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    publicDir: 'public',
    server: {
      allowedHosts: true,
      proxy: {
        '/api': {
          target: 'https://gitrec.gorse.io',
          changeOrigin: true,
          configure: (proxy) => {
            proxy.on('proxyReq', (proxyReq) => {
              if (devProxyCookie) {
                proxyReq.setHeader('Cookie', devProxyCookie)
              }
            })
          },
        },
      },
    },
  }
})
