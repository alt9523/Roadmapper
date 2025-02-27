// Custom Ajv configuration to avoid bundling issues
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

function createAjv() {
  const ajv = new Ajv({
    allErrors: true,
    strict: false,
    strictSchema: false
  });
  
  addFormats(ajv);
  return ajv;
}

module.exports = createAjv; 