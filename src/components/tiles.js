// Tile rendering functions
const { navStack } = require('../utils/navigation');

/**
 * Creates a program tile
 * @param {Object} program - The program object
 * @param {Function} clickHandler - The click handler function
 * @returns {HTMLElement} The program tile element
 */
function createProgramTile(program, clickHandler) {
  const tile = document.createElement("div");
  tile.className = "tile";
  tile.innerHTML = `<h3>${program.name}</h3>`;
  
  if (clickHandler) {
    tile.onclick = () => clickHandler(program);
  }
  
  return tile;
}

/**
 * Creates a product tile
 * @param {Object} product - The product object
 * @param {Function} clickHandler - The click handler function
 * @returns {HTMLElement} The product tile element
 */
function createProductTile(product, clickHandler) {
  const tile = document.createElement("div");
  tile.className = "tile";
  tile.setAttribute("data-product-id", product.id);
  
  tile.innerHTML = `<div class="tile-name">${product.name}</div>`;
  
  if (clickHandler) {
    tile.onclick = () => clickHandler(product);
  }
  
  return tile;
}

/**
 * Creates a material system tile
 * @param {Object} material - The material system object
 * @param {Function} clickHandler - The click handler function
 * @returns {HTMLElement} The material system tile element
 */
function createMaterialTile(material, clickHandler) {
  const tile = document.createElement("div");
  tile.className = "tile";
  tile.textContent = material.name;
  
  if (clickHandler) {
    tile.onclick = () => clickHandler(material);
  }
  
  return tile;
}

/**
 * Creates a supplier tile
 * @param {Object} supplier - The supplier object
 * @param {Function} clickHandler - The click handler function
 * @returns {HTMLElement} The supplier tile element
 */
function createSupplierTile(supplier, clickHandler) {
  const tile = document.createElement("div");
  tile.className = "tile";
  tile.textContent = supplier.name;
  
  if (clickHandler) {
    tile.onclick = () => clickHandler(supplier);
  }
  
  return tile;
}

/**
 * Creates a funding opportunity tile
 * @param {Object} opportunity - The funding opportunity object
 * @param {Function} clickHandler - The click handler function
 * @returns {HTMLElement} The funding opportunity tile element
 */
function createFundingOpportunityTile(opportunity, clickHandler) {
  const tile = document.createElement("div");
  tile.className = "tile";
  tile.textContent = opportunity.name;
  
  if (clickHandler) {
    tile.onclick = () => clickHandler(opportunity);
  }
  
  return tile;
}

module.exports = {
  createProgramTile,
  createProductTile,
  createMaterialTile,
  createSupplierTile,
  createFundingOpportunityTile
}; 