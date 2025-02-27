// Browser-compatible main entry point
document.addEventListener('DOMContentLoaded', function() {
  console.log('Interactive Roadmap initialized in browser');
  
  // Load data from a JSON file or API endpoint
  fetch('data/roadmap-data.json')
    .then(response => response.json())
    .then(data => {
      // No validation in browser version to avoid Ajv issues
      initializeRoadmap(data);
    })
    .catch(error => {
      console.error('Error loading roadmap data:', error);
    });
  
  function initializeRoadmap(data) {
    // Render the roadmap with the provided data
    const mainView = document.getElementById('mainView');
    if (mainView) {
      mainView.innerHTML = `<h2>Roadmap Data Loaded</h2>
        <p>Found ${data.programs ? data.programs.length : 0} programs</p>`;
    }
  }
});

// Export browser-compatible functions
window.InteractiveRoadmap = {
  // Public API methods here
  renderRoadmap: function(elementId, data) {
    const element = document.getElementById(elementId);
    if (element) {
      element.innerHTML = `<h2>Custom Roadmap</h2>
        <p>Rendering custom roadmap with ${data.programs ? data.programs.length : 0} programs</p>`;
    }
  }
}; 