const fs = require('fs');
const path = require('path');

// Ensure build directory exists
if (!fs.existsSync('build')) {
  fs.mkdirSync('build');
}

// List of files to concatenate in order
const files = [
  'src/config.js',
  'src/schema.js',
  'src/utils/dateUtils.js',
  'src/utils/domUtils.js',
  'src/utils/navigation.js',
  'src/components/tiles.js',
  'src/components/roadmap.js',
  'src/views/detailViews.js',
  'src/views/mainViews.js',
  'src/html/template.js',
  'src/main.js'
];

// Create a global object to store all modules
let output = `
// Global object to store all modules
const modules = {};

`;

// Process each file
files.forEach(file => {
  console.log(`Processing ${file}...`);
  try {
    let content = fs.readFileSync(file, 'utf8');
    
    // Get module name from file path
    const moduleName = path.basename(path.dirname(file)) === 'src' 
      ? path.basename(file, '.js')
      : path.basename(path.dirname(file)) + '_' + path.basename(file, '.js');
    
    // Replace require statements with references to our modules object
    content = content.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*require\(['"]\.\.\/utils\/dateUtils['"]\);/g, 
      "const { $1 } = modules.dateUtils;");
    
    content = content.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*require\(['"]\.\.\/utils\/navigation['"]\);/g, 
      "const { $1 } = modules.navigation;");
    
    content = content.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*require\(['"]\.\.\/utils\/domUtils['"]\);/g, 
      "const { $1 } = modules.domUtils;");
    
    content = content.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*require\(['"]\.\.\/components\/roadmap['"]\);/g, 
      "const { $1 } = modules.components_roadmap;");
    
    content = content.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*require\(['"]\.\.\/views\/mainViews['"]\);/g, 
      "const { $1 } = modules.views_mainViews;");
    
    content = content.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*require\(['"]\.\.\/views\/detailViews['"]\);/g, 
      "const { $1 } = modules.views_detailViews;");
    
    content = content.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*require\(['"]\.\.\/html\/template['"]\);/g, 
      "const { $1 } = modules.html_template;");
    
    // Replace module.exports with assignment to modules object
    content = content.replace(/module\.exports\s*=\s*{([^}]+)}/g, 
      `modules.${moduleName} = {$1}`);
    
    // Wrap in IIFE to create proper scope
    output += `
// ${file}
(function() {
${content}
})();

`;
  } catch (err) {
    console.error(`Error reading file ${file}: ${err.message}`);
    process.exit(1);
  }
});

// Add the main execution code
output += `
// Execute main function
modules.main.buildHTML();
`;

try {
  fs.writeFileSync('build/interactiveRoadmap.js', output);
  console.log('Build complete! Output written to build/interactiveRoadmap.js');
} catch (err) {
  console.error(`Error writing output file: ${err.message}`);
  process.exit(1);
} 