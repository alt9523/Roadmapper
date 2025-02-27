/**
 * JavaScript functions for the interactive roadmap
 * @param {string} roadmapDataStr - JSON string of the roadmap data
 * @returns {string} JavaScript code as a string
 */
function getScripts(roadmapDataStr) {
  return `
// Navigation stack to track view history
const navStack = [];

// Store the data for client-side use
let roadmapData;
try {
  // Safely parse the JSON data
  roadmapData = JSON.parse('${roadmapDataStr}');
  console.log('Roadmap data loaded successfully');
  
  // Debug the data structure
  console.log('Programs:', roadmapData.programs ? roadmapData.programs.length : 0);
  console.log('Products:', roadmapData.products ? roadmapData.products.length : 0);
  console.log('Material Systems:', roadmapData.materialSystems ? roadmapData.materialSystems.length : 0);
  console.log('Suppliers:', roadmapData.suppliers ? roadmapData.suppliers.length : 0);
  console.log('Funding Opportunities:', roadmapData.cradOpportunities ? roadmapData.cradOpportunities.length : 0);
  
  // Log the first program if available
  if (roadmapData.programs && roadmapData.programs.length > 0) {
    console.log('First program:', roadmapData.programs[0]);
  }
} catch (error) {
  console.error('Error parsing roadmap data:', error);
  console.error('Raw data:', '${roadmapDataStr.substring(0, 100)}...');
  roadmapData = { programs: [], products: [], materialSystems: [], suppliers: [], cradOpportunities: [] };
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM fully loaded');
  
  // Debug the navigation tabs
  debugElement('.nav-tab');
  
  // Debug the views
  debugElement('.detail-view');
  debugElement('#mainView');
  
  initializeNavigation();
  attachEventHandlers();
  setupSearch();
  addTooltips();
  
  // Set default view
  const defaultTab = document.querySelector('.nav-tab[data-view="programsView"]');
  if (defaultTab) {
    console.log('Setting default tab:', defaultTab);
    defaultTab.classList.add('active');
    showView('programsView');
  } else {
    console.error('Default tab not found');
  }
});

// Set up navigation and event handlers
function initializeNavigation() {
  console.log('Initializing navigation');
  
  // Set up navigation tabs
  document.querySelectorAll('.nav-tab').forEach(tab => {
    const viewId = tab.getAttribute('data-view');
    console.log('Setting up tab for view:', viewId);
    
    tab.addEventListener('click', function(e) {
      console.log('Tab clicked:', viewId);
      e.preventDefault();
      
      // Update active tab
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      // Show the selected view
      showView(viewId);
    });
  });
  
  // Add keyboard navigation
  document.addEventListener('keydown', function(e) {
    // ESC key for going back
    if (e.key === 'Escape') {
      goBack();
    }
  });
  
  // Set up back buttons
  document.querySelectorAll('.back-button').forEach(button => {
    button.addEventListener('click', function(e) {
      console.log('Back button clicked');
      e.preventDefault();
      goBack();
    });
  });
}

// Attach event handlers to all interactive elements
function attachEventHandlers() {
  console.log('Attaching event handlers');
  
  // Set up program tile click handlers
  document.querySelectorAll('[data-program-id]').forEach(tile => {
    const programId = tile.getAttribute('data-program-id');
    console.log('Setting up click handler for program:', programId);
    
    tile.addEventListener('click', function() {
      const programId = this.getAttribute('data-program-id');
      console.log('Program tile clicked:', programId);
      
      // Debug the roadmapData object
      console.log('Roadmap data programs:', roadmapData.programs);
      
      const program = roadmapData.programs.find(p => p.id === programId);
      console.log('Found program:', program);
      
      if (program) {
        showProgramDetails(program);
      } else {
        console.error('Program not found:', programId);
        console.error('Available program IDs:', roadmapData.programs.map(p => p.id));
      }
    });
  });
  
  // Set up product tile click handlers
  document.querySelectorAll('[data-product-id]').forEach(tile => {
    const productId = tile.getAttribute('data-product-id');
    console.log('Setting up click handler for product:', productId);
    
    tile.addEventListener('click', function() {
      const productId = this.getAttribute('data-product-id');
      console.log('Product tile clicked:', productId);
      
      // Debug the roadmapData object
      console.log('Roadmap data products:', roadmapData.products);
      
      const product = roadmapData.products.find(p => p.id === productId);
      console.log('Found product:', product);
      
      if (product) {
        showProductDetails(product);
      } else {
        console.error('Product not found:', productId);
        console.error('Available product IDs:', roadmapData.products.map(p => p.id));
      }
    });
  });
  
  // Set up material system tile click handlers
  document.querySelectorAll('[data-material-id]').forEach(tile => {
    tile.addEventListener('click', function() {
      const materialId = this.getAttribute('data-material-id');
      console.log('Material tile clicked:', materialId);
      
      const material = roadmapData.materialSystems.find(m => m.id === materialId);
      if (material) {
        showMaterialSystemDetails(material);
      }
    });
  });
  
  // Set up supplier tile click handlers
  document.querySelectorAll('[data-supplier-id]').forEach(tile => {
    tile.addEventListener('click', function() {
      const supplierId = this.getAttribute('data-supplier-id');
      console.log('Supplier tile clicked:', supplierId);
      
      const supplier = roadmapData.suppliers.find(s => s.id === supplierId);
      if (supplier) {
        showSupplierDetails(supplier);
      }
    });
  });
  
  // Set up funding opportunity tile click handlers
  document.querySelectorAll('[data-opportunity-id]').forEach(tile => {
    tile.addEventListener('click', function() {
      const opportunityId = this.getAttribute('data-opportunity-id');
      console.log('Opportunity tile clicked:', opportunityId);
      
      const opportunity = roadmapData.cradOpportunities.find(o => o.id === opportunityId);
      if (opportunity) {
        showFundingOpportunityDetails(opportunity);
      }
    });
  });
}

// Add tooltips to navigation tabs
function addTooltips() {
  document.querySelectorAll('.nav-tab').forEach(tab => {
    const viewId = tab.getAttribute('data-view');
    let tooltipText = '';
    
    switch(viewId) {
      case 'programsView':
        tooltipText = 'View all programs and their timelines';
        break;
      case 'productsView':
        tooltipText = 'View products and their associated programs';
        break;
      case 'amMaterialSystemsView':
        tooltipText = 'View additive manufacturing material systems';
        break;
      case 'amSuppliersView':
        tooltipText = 'View suppliers for AM materials';
        break;
      case 'fundingOpportunitiesView':
        tooltipText = 'View funding opportunities';
        break;
    }
    
    if (tooltipText) {
      createTooltip(tab, tooltipText);
    }
  });
}

// Helper function for formatting dates
function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

// Navigation functions
function showView(viewId) {
  console.log('Showing view:', viewId);
  
  // Hide all views
  document.querySelectorAll('.detail-view, .main-content').forEach(view => {
    view.style.display = 'none';
  });
  
  // Show the requested view
  const viewElement = document.getElementById(viewId);
  if (viewElement) {
    viewElement.style.display = 'block';
    console.log('View displayed:', viewId);
    
    // Update navigation stack
    navStack.push(viewId);
    console.log('Navigation stack:', navStack);
  } else {
    console.error('View not found:', viewId);
    // List all available views
    console.log('Available views:');
    document.querySelectorAll('.detail-view, .main-content').forEach(view => {
      console.log('- ' + view.id);
    });
  }
}

function goBack() {
  console.log('Going back. Current stack:', navStack);
  
  if (navStack.length > 1) {
    navStack.pop(); // Remove current view
    const previousView = navStack[navStack.length - 1];
    
    // Hide all views
    document.querySelectorAll('.detail-view, .main-content').forEach(view => {
      view.style.display = 'none';
    });
    
    // Show the previous view
    document.getElementById(previousView).style.display = 'block';
    console.log('Returned to view:', previousView);
  } else {
    // If at the root level, show main view
    document.querySelectorAll('.detail-view').forEach(view => {
      view.style.display = 'none';
    });
    document.getElementById('mainView').style.display = 'block';
    navStack.length = 0; // Clear the stack
    console.log('Returned to main view');
  }
}

// Add a helper function to create tooltips
function createTooltip(element, text) {
  element.classList.add('tooltip');
  const tooltipSpan = document.createElement('span');
  tooltipSpan.className = 'tooltip-text';
  tooltipSpan.textContent = text;
  element.appendChild(tooltipSpan);
}

// Add search functionality
function setupSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) {
    console.warn('Search input not found');
    return;
  }
  
  console.log('Setting up search functionality');
  searchInput.addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    console.log('Searching for:', searchTerm);
    
    // Search in all tiles
    document.querySelectorAll('.tile').forEach(tile => {
      const tileName = tile.querySelector('.tile-name').textContent.toLowerCase();
      const tileDesc = tile.querySelector('.tile-description')?.textContent.toLowerCase() || '';
      
      if (tileName.includes(searchTerm) || tileDesc.includes(searchTerm)) {
        tile.style.display = 'block';
      } else {
        tile.style.display = 'none';
      }
    });
  });
}

// Debug function to help troubleshoot
function debugElement(selector) {
  const elements = document.querySelectorAll(selector);
  console.log(\`Found \${elements.length} elements matching "\${selector}"\`);
  elements.forEach((el, i) => {
    console.log(\`Element \${i}:\`, el);
    if (el.id) {
      console.log(\`  ID: \${el.id}\`);
    }
    if (el.className) {
      console.log(\`  Classes: \${el.className}\`);
    }
    if (el.getAttribute('data-view')) {
      console.log(\`  View: \${el.getAttribute('data-view')}\`);
    }
  });
}

// Add a global error handler to catch any JavaScript errors
window.onerror = function(message, source, lineno, colno, error) {
  console.error('JavaScript error:', message);
  console.error('Source:', source);
  console.error('Line:', lineno, 'Column:', colno);
  console.error('Error object:', error);
  return true;
};
`;
}

module.exports = { getScripts }; 