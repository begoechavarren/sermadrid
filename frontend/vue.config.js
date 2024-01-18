const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  transpileDependencies: true,

  pages: {
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
      title: 'sermadrid',
    },
  },

  chainWebpack: config => {
    // Add a new rule for .geojson files
    config.module
      .rule('geojson')
      .test(/\.geojson$/)
      .use('json-loader')
        .loader('json-loader')
        .end();
  }
});
