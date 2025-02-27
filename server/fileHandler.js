const fs = require('fs');
const path = require('path');

const JSON_FILE_PATH = path.join(__dirname, '..', 'roadmap.json');

function readJsonFile() {
  try {
    return JSON.parse(fs.readFileSync(JSON_FILE_PATH, 'utf8'));
  } catch (error) {
    console.error('Error reading JSON file:', error);
    throw error;
  }
}

function writeJsonFile(data) {
  try {
    fs.writeFileSync(JSON_FILE_PATH, JSON.stringify(data, null, 2), 'utf8');
    return { success: true };
  } catch (error) {
    console.error('Error writing JSON file:', error);
    throw error;
  }
}

module.exports = {
  readJsonFile,
  writeJsonFile
}; 