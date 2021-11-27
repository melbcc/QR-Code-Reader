module.exports = {
  css: {
    loaderOptions: {
      less: {
        lessOptions: {
          javascriptEnabled: true,
        },
      },
    },
  },
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      "/api": {
        target: `http://${process.env.API_HOST || "127.0.0.1:8080"}`,
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
      },
      "/token": {
        target: `http://${process.env.API_HOST || "127.0.0.1:8080"}`,
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
      },
    },
    progress: false, // ref: https://github.com/vuejs/vue-cli/issues/4557#issuecomment-545965828
  },
  outputDir: process.env.VUE_OUTPUT_DIR || "dist",
  publicPath: process.env.VUE_PUBLIC_PATH || '/',
};
