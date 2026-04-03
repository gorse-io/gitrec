const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  publicPath: '/',
  outputDir: 'dist',
  devServer: {
    allowedHosts: 'all',
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
      },
      "/login": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
      },
      "/logout": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
      },
    }
  },
});
