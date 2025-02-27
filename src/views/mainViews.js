// Main tab views (Programs, Products, etc.)
const { navStack } = require('../utils/navigation');

/**
 * Render the programs view
 * @param {Object} data - The roadmap data
 */
function renderPrograms(data) {
  const mainView = document.getElementById('mainView');
  if (!mainView) return;
  
  // Clear the view
  mainView.innerHTML = '';
  
  // Create header
  const header = document.createElement('h2');
  header.textContent = 'Programs';
  mainView.appendChild(header);
  
  // Check if there are programs
  if (!data.programs || data.programs.length === 0) {
    const noData = document.createElement('p');
    noData.textContent = 'No programs available.';
    mainView.appendChild(noData);
    return;
  }
  
  // Create program tiles
  data.programs.forEach(program => {
    const tile = document.createElement('div');
    tile.className = 'tile';
    tile.innerHTML = `<h2>${program.name}</h2>`;
    
    tile.onclick = function() {
      console.log('Program tile clicked:', program);
      navStack.push('programsView');
      loadProgramDetails(program);
    };
    
    mainView.appendChild(tile);
  });
}

/**
 * Render the products view
 * @param {Object} data - The roadmap data
 */
function renderProducts(data) {
  const productsView = document.getElementById('productsView');
  if (!productsView) return;
  
  let html = '<h2>Products</h2>\n    <div class="tiles-container">';
  
  data.products.forEach(product => {
    html += `
      <div class="tile" data-product-id="${product.id}">
        <div class="tile-name">${product.name}</div>
      </div>`;
  });
  
  html += '</div>';
  productsView.innerHTML = html;
  
  // Add click handlers
  productsView.querySelectorAll('.tile').forEach(tile => {
    tile.addEventListener('click', function() {
      const productId = this.getAttribute('data-product-id');
      const product = data.products.find(p => p.id === productId);
      
      if (product) {
        navStack.push('productsView');
        loadProductDetails(product);
      }
    });
  });
}

/**
 * Render the AM material systems view
 * @param {Object} data - The roadmap data
 */
function renderAMMaterialSystems(data) {
  const materialSystemsView = document.getElementById('amMaterialSystemsView');
  if (!materialSystemsView) return;
  
  materialSystemsView.innerHTML = '';
  
  data.materialSystems.forEach(material => {
    const tile = document.createElement('div');
    tile.className = 'tile';
    tile.textContent = material.name;
    
    tile.onclick = function() {
      navStack.push('amMaterialSystemsView');
      loadMaterialDetails(material);
    };
    
    materialSystemsView.appendChild(tile);
  });
}

/**
 * Render the AM suppliers view
 * @param {Object} data - The roadmap data
 */
function renderAMSuppliers(data) {
  const suppliersView = document.getElementById('amSuppliersView');
  if (!suppliersView) return;
  
  suppliersView.innerHTML = '';
  
  data.suppliers.forEach(supplier => {
    const tile = document.createElement('div');
    tile.className = 'tile';
    tile.textContent = supplier.name;
    
    tile.onclick = function() {
      navStack.push('amSuppliersView');
      loadSupplierDetails(supplier);
    };
    
    suppliersView.appendChild(tile);
  });
}

/**
 * Render the funding opportunities view
 * @param {Object} data - The roadmap data
 */
function renderFundingOpportunities(data) {
  const opportunitiesView = document.getElementById('fundingOpportunitiesView');
  if (!opportunitiesView) return;
  
  opportunitiesView.innerHTML = '';
  
  data.cradOpportunities.forEach(opportunity => {
    const tile = document.createElement('div');
    tile.className = 'tile';
    tile.textContent = opportunity.name;
    
    tile.onclick = function() {
      navStack.push('fundingOpportunitiesView');
      loadOpportunityDetails(opportunity);
    };
    
    opportunitiesView.appendChild(tile);
  });
}

module.exports = {
  renderPrograms,
  renderProducts,
  renderAMMaterialSystems,
  renderAMSuppliers,
  renderFundingOpportunities
}; 