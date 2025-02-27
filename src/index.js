const fs = require('fs');
const path = require('path');
const { generateHtmlContent } = require('./html/template');

// Load the data from the JSON file
function loadRoadmapData() {
  try {
    const dataPath = path.join(__dirname, '../data/roadmap-data.json');
    console.log('Loading data from:', dataPath);
    
    if (fs.existsSync(dataPath)) {
      const rawData = fs.readFileSync(dataPath, 'utf8');
      const data = JSON.parse(rawData);
      console.log('Data loaded successfully');
      console.log('Programs:', data.programs ? data.programs.length : 0);
      return data;
    } else {
      console.error('Data file not found:', dataPath);
      return null;
    }
  } catch (error) {
    console.error('Error loading roadmap data:', error);
    return null;
  }
}

// Generate the HTML content
function generateRoadmap() {
  const data = loadRoadmapData();
  if (!data) {
    console.error('Failed to load roadmap data');
    return 'Error: Failed to load roadmap data';
  }
  
  return generateHtmlContent(data);
}

module.exports = { generateRoadmap }; 