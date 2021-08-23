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
    https: true, // required to enable camera
  },
};
