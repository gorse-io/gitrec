const glob = require("glob");
const pages = {};

glob.sync("./src/**/main.js").forEach((path) => {
  const chunk = path.split("./src/")[1].split("/main.js")[0];
  pages[chunk] = {
    entry: path,
    template: "public/index.html",
    chunks: ["chunk-vendors", "chunk-common", chunk],
  };
});
module.exports = {
  pages,
  transpileDependencies: ['vuetify'],
  chainWebpack: (config) => config.plugins.delete("named-chunks"),
  devServer: {
    allowedHosts: 'all',
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
      },
    }
  },
};
