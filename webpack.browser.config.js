const path = require('path');

module.exports = {
  entry: './src/browser-main.js',
  output: {
    filename: 'interactiveRoadmap.browser.js',
    path: path.resolve(__dirname, 'build'),
    library: 'InteractiveRoadmap',
    libraryTarget: 'umd',
    globalObject: 'this'
  },
  target: 'web',
  mode: 'production',
  resolve: {
    fallback: {
      fs: false,
      path: false,
      os: false,
      ajv: false
    }
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  },
  externals: {
    ajv: 'Ajv'
  },
  devtool: 'source-map'
}; 