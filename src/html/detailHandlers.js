/**
 * JavaScript functions for handling detailed views in the interactive roadmap
 * @returns {string} JavaScript code as a string
 */
const { generateRoadmapHtml } = require('./roadmap');
const { getRoadmapVisualizer } = require('./visualizations/roadmapVisualizer');
const { getQuadBoxVisualizer } = require('./visualizations/quadBoxVisualizer');
const { getProgramHandler } = require('./handlers/programHandler');
const { getProductHandler } = require('./handlers/productHandler');
const { getMaterialHandler } = require('./handlers/materialHandler');
const { getSupplierHandler } = require('./handlers/supplierHandler');
const { getFormatters } = require('./utils/formatters');

function getAllDetailHandlers() {
  return `
// Create a navigation namespace to avoid conflicts
const Navigation = {
  stack: [],
  
  push: function(view) {
    this.stack.push(view);
    console.log('Navigation stack updated:', this.stack);
  },
  
  goBack: function() {
    if (this.stack.length > 0) {
      const prevView = this.stack.pop();
      console.log('Going back to:', prevView);
      
      // Show the previous view
      if (prevView === 'mainView') {
        this.showView('mainView');
      } else if (prevView === 'programDetailsView') {
        this.showView('programDetailsView');
      } else if (prevView === 'productDetailsView') {
        this.showView('productDetailsView');
      } else if (prevView === 'materialDetailSection') {
        document.querySelectorAll('.detail-view').forEach(view => {
          view.style.display = 'none';
        });
        document.getElementById('materialDetailSection').style.display = 'block';
      } else if (prevView === 'supplierDetailSection') {
        document.querySelectorAll('.detail-view').forEach(view => {
          view.style.display = 'none';
        });
        document.getElementById('supplierDetailSection').style.display = 'block';
      }
    } else {
      // If no previous view, go to main view
      this.showView('programsView'); // Default to programs view
    }
  },
  
  showView: function(viewId) {
    console.log('Showing view:', viewId);
    
    // First, hide all detail views
    document.querySelectorAll('.detail-view').forEach(view => {
      view.style.display = 'none';
    });
    
    // Hide welcome message if it exists
    const welcomeHeadings = document.querySelectorAll('h1, h2, h3');
    welcomeHeadings.forEach(heading => {
      if (heading.textContent.includes('Welcome to the Interactive Roadmap')) {
        // Find a parent container to hide
        let parent = heading;
        // Go up to find a suitable container
        while (parent && !parent.classList.contains('container') && parent.parentElement) {
          parent = parent.parentElement;
        }
        
        // If we found a suitable container that's not the main container, hide it
        if (parent && !parent.classList.contains('container')) {
          parent.style.display = 'none';
        } else if (heading.parentElement) {
          // Otherwise just hide the heading's parent
          heading.parentElement.style.display = 'none';
        }
      }
    });
    
    // Show the requested view
    const targetView = document.getElementById(viewId);
    if (targetView) {
      targetView.style.display = 'block';
    } else {
      console.error('Target view not found:', viewId);
      // Show the programs view as a fallback
      const programsView = document.getElementById('programsView');
      if (programsView) {
        programsView.style.display = 'block';
      }
    }
  }
};

// Define global functions that use our Navigation namespace
function goBack() { Navigation.goBack(); }
function showView(viewId) { Navigation.showView(viewId); }

// Import utility functions first
${getFormatters()}

// Import visualizations next - before handlers that use them
${getRoadmapVisualizer()}
${getQuadBoxVisualizer()}

// Import handlers last - after the visualizations they depend on
${getProgramHandler().replace(/navStack\.push/g, 'Navigation.stack.push')}
${getProductHandler().replace(/navStack\.push/g, 'Navigation.stack.push')}
${getMaterialHandler().replace(/navStack\.push/g, 'Navigation.stack.push')}
${getSupplierHandler().replace(/navStack\.push/g, 'Navigation.stack.push')}

// Initialize by hiding welcome section when any tab is clicked
document.addEventListener('DOMContentLoaded', function() {
  // Add click handlers to the navigation tabs
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const viewId = this.getAttribute('data-view');
      if (viewId) {
        showView(viewId);
      }
    });
  });
  
  // Add any other initialization for new handlers here
  // For example, initialize supplier view handlers
  const supplierLinks = document.querySelectorAll('.supplier-link');
  supplierLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const supplierId = this.getAttribute('data-supplier-id');
      const supplier = roadmapData.suppliers.find(s => s.id === supplierId);
      if (supplier) {
        showSupplierDetails(supplier);
      }
    });
  });
  
  // Log that initialization is complete
  console.log('Detail handlers initialized successfully');
});
`;
}

module.exports = { getAllDetailHandlers };