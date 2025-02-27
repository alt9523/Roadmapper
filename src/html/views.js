/**
 * HTML templates for the different views in the interactive roadmap
 */
const { sanitizeData } = require('../utils/templateUtils');

/**
 * Generates the HTML for the main navigation and container
 * @returns {string} HTML for the main structure
 */
function getMainStructure() {
  return `
<header>
  <h1>Interactive Roadmap</h1>
</header>

<div class="container">
  <div class="nav-tabs">
    <div class="nav-tab" data-view="programsView">Programs</div>
    <div class="nav-tab" data-view="productsView">Products</div>
    <div class="nav-tab" data-view="amMaterialSystemsView">AM Material Systems</div>
    <div class="nav-tab" data-view="amSuppliersView">AM Suppliers</div>
    <div class="nav-tab" data-view="fundingOpportunitiesView">Funding Opportunities</div>
  </div>
  
  <div id="searchContainer" style="margin: 20px 0;">
    <input type="text" id="searchInput" placeholder="Search..." style="padding: 8px; width: 100%; border: 1px solid #ddd; border-radius: 4px;">
  </div>
  
  <div id="mainView" class="main-content" style="display: block;">
    <h2>Welcome to the Interactive Roadmap</h2>
    <p>Use the navigation tabs above to explore different sections of the roadmap.</p>
  </div>
`;
}

/**
 * Generates the HTML for the programs view
 * @param {Object} data - The roadmap data
 * @returns {string} HTML for the programs view
 */
function getProgramsView(data) {
  const safeData = sanitizeData(data);
  
  return `
<div id="programsView" class="detail-view">
  <div class="detail-header">
    <h2>Programs</h2>
    <button class="back-button">Back</button>
  </div>
  <div class="tiles-container">
    ${safeData.programs.map(program => `
      <div class="tile" data-program-id="${program.id}">
        <div class="tile-name">${program.name}</div>
        <div class="tile-description">${program.description || 'No description available'}</div>
        <div class="tile-status">
          <strong>Status:</strong> 
          <span class="status-indicator status-${program.status ? program.status.toLowerCase().replace(/\s+/g, '-') : 'planned'}"></span>
          ${program.status || 'Planned'}
        </div>
      </div>
    `).join('')}
  </div>
</div>

<div id="programDetailsView" class="detail-view">
  <div id="programDetailsContent"></div>
</div>
`;
}

/**
 * Generates the HTML for the products view
 * @param {Object} data - The roadmap data
 * @returns {string} HTML for the products view
 */
function getProductsView(data) {
  const safeData = sanitizeData(data);
  
  return `
<div id="productsView" class="detail-view">
  <div class="detail-header">
    <h2>Products</h2>
    <button class="back-button">Back</button>
  </div>
  <div class="tiles-container">
    ${safeData.products.map(product => `
      <div class="tile" data-product-id="${product.id}">
        <div class="tile-name">${product.name}</div>
        <div class="tile-programs">
          <strong>Programs:</strong> 
          ${product.programs && product.programs.length > 0 
            ? product.programs.map(progId => {
                const prog = safeData.programs.find(p => p.id === progId);
                return prog ? prog.name : progId;
              }).join(', ') 
            : 'None'}
        </div>
      </div>
    `).join('')}
  </div>
</div>

<div id="productDetailsView" class="detail-view">
  <div class="detail-header">
    <h2>Product Details</h2>
    <button class="back-button">Back</button>
  </div>
  <div id="productDetails"></div>
  <div id="productPrograms" class="related-items-container"></div>
  <div id="productQuadBox" class="quad-box-wrapper"></div>
</div>
`;
}

/**
 * Generates the HTML for the material systems view
 * @param {Object} data - The roadmap data
 * @returns {string} HTML for the material systems view
 */
function getMaterialSystemsView(data) {
  const safeData = sanitizeData(data);
  
  return `
<div id="amMaterialSystemsView" class="detail-view">
  <div class="detail-header">
    <h2>AM Material Systems</h2>
    <button class="back-button">Back</button>
  </div>
  <div class="tiles-container">
    ${safeData.materialSystems.map(material => `
      <div class="tile" data-material-id="${material.id}">
        <div class="tile-name">${material.name}</div>
        <div class="tile-qualification">
          <strong>Qualification:</strong> ${material.qualification || 'N/A'}
        </div>
        <div class="tile-qualification-class">
          <strong>Class:</strong> ${material.qualificationClass || 'N/A'}
        </div>
      </div>
    `).join('')}
  </div>
</div>

<div id="materialSystemDetailsView" class="detail-view">
  <div class="detail-header">
    <h2>Material System Details</h2>
    <button class="back-button">Back</button>
  </div>
  <div id="materialSystemDetails"></div>
  <div id="materialSystemSuppliers" class="related-items-container"></div>
</div>
`;
}

/**
 * Generates the HTML for the suppliers view
 * @param {Object} data - The roadmap data
 * @returns {string} HTML for the suppliers view
 */
function getSuppliersView(data) {
  const safeData = sanitizeData(data);
  
  return `
<div id="amSuppliersView" class="detail-view">
  <div class="detail-header">
    <h2>AM Suppliers</h2>
    <button class="back-button">Back</button>
  </div>
  <div class="tiles-container">
    ${safeData.suppliers.map(supplier => `
      <div class="tile" data-supplier-id="${supplier.id}">
        <div class="tile-name">${supplier.name}</div>
        <div class="tile-materials">
          <strong>Materials:</strong> ${supplier.materials && supplier.materials.length > 0 
            ? supplier.materials.map(matId => {
                const mat = safeData.materialSystems.find(m => m.id === matId);
                return mat ? mat.name : matId;
              }).join(', ') 
            : 'N/A'}
        </div>
      </div>
    `).join('')}
  </div>
</div>

<div id="supplierDetailsView" class="detail-view">
  <div class="detail-header">
    <h2>Supplier Details</h2>
    <button class="back-button">Back</button>
  </div>
  <div id="supplierDetails"></div>
  <div id="supplierMaterials" class="related-items-container"></div>
</div>
`;
}

/**
 * Generates the HTML for the funding opportunities view
 * @param {Object} data - The roadmap data
 * @returns {string} HTML for the funding opportunities view
 */
function getFundingOpportunitiesView(data) {
  const safeData = sanitizeData(data);
  
  return `
<div id="fundingOpportunitiesView" class="detail-view">
  <div class="detail-header">
    <h2>Funding Opportunities</h2>
    <button class="back-button">Back</button>
  </div>
  <div class="tiles-container">
    ${safeData.cradOpportunities.map(opportunity => `
      <div class="tile" data-opportunity-id="${opportunity.id}">
        <div class="tile-name">${opportunity.name}</div>
        <div class="tile-details">${opportunity.details || 'No details available'}</div>
        ${opportunity.deadline ? `
          <div class="tile-deadline">
            <strong>Deadline:</strong> ${new Date(opportunity.deadline).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
          </div>
        ` : ''}
      </div>
    `).join('')}
  </div>
</div>

<div id="fundingOpportunityDetailsView" class="detail-view">
  <div class="detail-header">
    <h2>Funding Opportunity Details</h2>
    <button class="back-button">Back</button>
  </div>
  <div id="fundingOpportunityDetails"></div>
  <div id="relatedEntities" class="related-items-container"></div>
</div>
`;
}

/**
 * Generates the HTML for the task details view
 * @returns {string} HTML for the task details view
 */
function getTaskDetailsView() {
  return `
<div id="taskDetailsView" class="detail-view">
  <div class="detail-header">
    <h2>Task Details</h2>
    <button class="back-button">Back</button>
  </div>
  <div id="taskDetails"></div>
</div>
`;
}

/**
 * Combines all views into a single HTML string
 * @param {Object} data - The roadmap data
 * @returns {string} Combined HTML for all views
 */
function getAllViews(data) {
  return `
${getMainStructure()}
${getProgramsView(data)}
${getProductsView(data)}
${getMaterialSystemsView(data)}
${getSuppliersView(data)}
${getFundingOpportunitiesView(data)}
${getTaskDetailsView()}
</div>`;
}

module.exports = {
  getMainStructure,
  getProgramsView,
  getProductsView,
  getMaterialSystemsView,
  getSuppliersView,
  getFundingOpportunitiesView,
  getTaskDetailsView,
  getAllViews
}; 