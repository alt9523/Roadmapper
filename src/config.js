// Configuration settings
const path = require('path');

// Define paths for data and output files
module.exports = {
  dataFilePath: path.resolve(__dirname, '../roadmap.json'),
  outputFilePath: path.resolve(__dirname, '../build/roadmap.html'),
  devRepoPath: path.resolve(__dirname, '../public'),
  devRepoOutputFilePath: path.resolve(__dirname, '../public/roadmap.html')
}; 