const path = require('path');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'interactiveRoadmap.js',
    path: path.resolve(__dirname, 'build'),
    libraryTarget: 'commonjs2'
  },
  target: 'node',
  mode: 'production',
  // Properly handle Node.js modules without webpack-node-externals
  externals: [
    /^(?!\.|\/).+/i,  // Exclude all node_modules
  ],
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
  // Add source maps for better debugging
  devtool: 'source-map',
  // Fix for __dirname and __filename in bundled code
  node: {
    __dirname: false,
    __filename: false,
  }
}; 