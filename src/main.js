// Main entry point
const fs = require('fs');
const path = require('path');
const { schema } = require('./schema');
const { generateHtmlContent } = require('./html/template');
const { dataFilePath, outputFilePath, devRepoPath, devRepoOutputFilePath } = require('./config');
const createAjv = require('./utils/ajv-config');
const { getAllDetailHandlers } = require('./html/detailHandlers');

// Create an Ajv instance
const ajv = createAjv();

function buildHTML() {
  try {
    const data = JSON.parse(fs.readFileSync(dataFilePath, "utf8"));
    const validateData = ajv.compile(schema);
    const valid = validateData(data);
    
    if (!valid) {
      console.error("Data validation error: " + JSON.stringify(validateData.errors, null, 2));
      return;
    }
    
    console.log("Data validation successful.");
    const htmlContent = generateHtmlContent(data);
    const detailHandlersJs = getAllDetailHandlers();
    fs.writeFileSync(outputFilePath, htmlContent, "utf8");
    console.log("HTML file generated successfully at: " + outputFilePath);
    copyToRepository();
    console.log('HTML file generated successfully!');
  } catch (err) {
    console.error("Error reading data file: " + err);
  }
}

function copyToRepository() {
  try {
    if (!fs.existsSync(devRepoPath)) {
      fs.mkdirSync(devRepoPath, { recursive: true });
      console.log("Created repository folder: " + devRepoPath);
    }
    fs.copyFileSync(outputFilePath, devRepoOutputFilePath);
    console.log("File copied successfully to external repository: " + devRepoOutputFilePath);
  } catch (err) {
    console.error("Error copying file to external repository: " + err);
  }
}

// Export functions for testing
module.exports = {
  buildHTML,
  copyToRepository
};

// Main execution
if (require.main === module) {
  buildHTML();
  
  // Watch for changes
  fs.watch(dataFilePath, function(eventType, filename) {
    if (filename && eventType === "change") {
      console.log(filename + " has been modified. Regenerating HTML and copying to external repository...");
      buildHTML();
    }
  });
} 