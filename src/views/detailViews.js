// Detail views (Program details, Product details, etc.)
const { navStack } = require('../utils/navigation');
const { formatDate, getStatusColor } = require('../utils/dateUtils');
const { renderProductRoadmap, updateRoadmapMaterialTasks } = require('../components/roadmap');
const { createTaskDetailSection } = require('../utils/domUtils');

// Program details function is already implemented

function loadProductDetails(product, roadmapData) {
  const detail = document.getElementById("productDetailSection");
  
  // Create the basic product information section
  let html = `
    <h2>${product.name}</h2>
    
    <h3>Overview</h3>
    <p><strong>Programs:</strong> ${roadmapData.programs
      .filter(p => product.programs.includes(p.id))
      .map(p => p.name)
      .join(", ")}</p>
    
    <h3>Requirements</h3>
    <div class="requirements-section">`;
  
  // Add requirements if they exist
  if (product.requirements) {
    html += `<ul>`;
    Object.values(product.requirements).forEach(value => {
      html += `<li>${value}</li>`;
    });
    html += `</ul>`;
  } else {
    html += `<p>No specific requirements defined.</p>`;
  }
  
  html += `</div>
    
    <div class="quad-layout">
      <!-- First quad box: Material Systems -->
      <div class="quad-box">
        <h3>Material Systems</h3>
        <div class="material-section">`;
  
  // Add material system filter buttons
  if (product.materialSystems && product.materialSystems.length > 0) {
    html += `<div class="material-filter">`;
    
    // Add material system buttons
    product.materialSystems.forEach((msId, index) => {
      const material = roadmapData.materialSystems.find(ms => ms.id === msId);
      if (material) {
        // Make the first material system active by default
        const isActive = index === 0 ? 'active' : '';
        html += `<span class="material-filter-btn ${isActive}" data-filter="${material.id}">${material.name}</span>`;
      }
    });
    
    html += `</div>`;
    
    // Add a single "View Additional Details" button
    html += `<div class="material-details-link">
      <span class="material-details-btn" id="view-material-details">View Additional Details</span>
    </div>`;
    
    // Add qualification and qualification class information from the material system
    product.materialSystems.forEach((msId, index) => {
      const material = roadmapData.materialSystems.find(ms => ms.id === msId);
      if (material) {
        // Only show the first material system's info by default
        const displayStyle = index === 0 ? 'block' : 'none';
        
        // Add qualification information
        html += `
          <div class="qualification-info material-specific" data-material="${material.id}" style="display: ${displayStyle};">
            <h4>Qualification</h4>
            <p><strong>Status:</strong> ${material.qualification || 'N/A'}</p>
            <p><strong>Class:</strong> ${material.qualificationClass || 'N/A'}</p>
          </div>`;
          
        // Add heat treatment information from the material system
        if (material.heatTreatment) {
          html += `
            <div class="heat-treat-info material-specific" data-material="${material.id}" style="display: ${displayStyle};">
              <h4>Heat Treatment</h4>`;
              
          if (typeof material.heatTreatment === 'object') {
            // Display heat treatment properties as a simple list without subheaders
            const heatTreatProps = [];
            if (material.heatTreatment.process) heatTreatProps.push(material.heatTreatment.process);
            if (material.heatTreatment.temperature) heatTreatProps.push(material.heatTreatment.temperature);
            if (material.heatTreatment.cooling) heatTreatProps.push(material.heatTreatment.cooling);
            
            if (heatTreatProps.length > 0) {
              html += `<ul>`;
              heatTreatProps.forEach(prop => {
                html += `<li>${prop}</li>`;
              });
              html += `</ul>`;
            } else {
              html += `<p>No specific heat treatment details available.</p>`;
            }
          } else {
            html += `<p>${material.heatTreatment}</p>`;
          }
          
          html += `</div>`;
        } else if (material.processingParameters && material.processingParameters.heatTreatment) {
          html += `
            <div class="heat-treat-info material-specific" data-material="${material.id}" style="display: ${displayStyle};">
              <h4>Heat Treatment</h4>
              <p>${material.processingParameters.heatTreatment}</p>
            </div>`;
        }
      }
    });
  } else {
    html += `<p>No material systems associated with this product.</p>`;
  }
  
  // Add heat treatment information from the product (if not already provided by material system)
  if (product.heatTreat && (!product.materialSystems || product.materialSystems.length === 0)) {
    html += `
      <div class="heat-treat-info">
        <h4>Heat Treatment</h4>
        <p><strong>Process:</strong> ${product.heatTreat.process || 'N/A'}</p>
        <p><strong>Temperature:</strong> ${product.heatTreat.temperature || 'N/A'}</p>
        <p><strong>Cooling:</strong> ${product.heatTreat.cooling || 'N/A'}</p>
      </div>`;
  }
  
  // Add post-processing information
  if (product.postProcessing && product.postProcessing.length > 0) {
    html += `
      <div class="post-processing-info">
        <h4>Post Processing</h4>
        <ul>`;
    
    product.postProcessing.forEach(process => {
      html += `<li>${process}</li>`;
    });
    
    html += `</ul>
      </div>`;
  }
  
  html += `</div>
      </div>
      
      <!-- Second quad box: Suppliers -->
      <div class="quad-box">
        <h3>Suppliers</h3>`;
  
  // Add relevant suppliers
  if (product.relevantSuppliers && product.relevantSuppliers.length > 0) {
    html += `<div class="supplier-tiles">`;
    
    product.relevantSuppliers.forEach(supplierId => {
      const supplier = roadmapData.suppliers.find(s => s.id === supplierId);
      if (supplier) {
        html += `<div class="supplier-tile" data-supplier-id="${supplier.id}">${supplier.name}</div>`;
      }
    });
    
    html += `</div>`;
  } else {
    html += `<p>No suppliers associated with this product.</p>`;
  }
  
  // Add post-processing suppliers if they exist
  if (product.postProcessingSuppliers && product.postProcessingSuppliers.length > 0) {
    html += `
      <h4>Post-Processing Suppliers</h4>
      <table class="post-processing-suppliers-table">
        <thead>
          <tr>
            <th>Process</th>
            <th>Supplier</th>
          </tr>
        </thead>
        <tbody>`;
    
    product.postProcessingSuppliers.forEach(pps => {
      const supplier = roadmapData.suppliers.find(s => s.id === pps.supplier);
      html += `
        <tr>
          <td>${pps.process}</td>
          <td><span class="supplier-link" data-supplier-id="${pps.supplier}">${supplier ? supplier.name : pps.supplier}</span></td>
        </tr>`;
    });
    
    html += `</tbody>
      </table>`;
  }
  
  html += `</div>
      
      <!-- Third quad box: Quality -->
      <div class="quad-box">
        <h3>Quality</h3>`;
  
  // Add NDT information
  if (product.ndt && product.ndt.length > 0) {
    html += `
      <div class="ndt-info">
        <h4>Non-Destructive Testing</h4>
        <ul>`;
    
    product.ndt.forEach(ndt => {
      html += `<li>${ndt}</li>`;
    });
    
    html += `</ul>
      </div>`;
  } else {
    // Check if the material system has NDT information
    let hasNDT = false;
    if (product.materialSystems && product.materialSystems.length > 0) {
      const firstMaterial = roadmapData.materialSystems.find(ms => ms.id === product.materialSystems[0]);
      if (firstMaterial && firstMaterial.standardNDT && firstMaterial.standardNDT.length > 0) {
        hasNDT = true;
        html += `
          <div class="ndt-info">
            <h4>Non-Destructive Testing (from Material System)</h4>
            <ul>`;
        
        firstMaterial.standardNDT.forEach(ndt => {
          html += `<li>${ndt}</li>`;
        });
        
        html += `</ul>
          </div>`;
      }
    }
    
    if (!hasNDT) {
      html += `<p>No NDT information available.</p>`;
    }
  }
  
  html += `</div>
      
      <!-- Fourth quad box: Implementation -->
      <div class="quad-box">
        <h3>Implementation</h3>`;
  
  // Add implementation status
  html += `<p><strong>Status:</strong> ${product.implementationStatus || 'N/A'}</p>`;
  
  // Add completion date if available
  if (product.completionDate) {
    html += `<p><strong>Completion Date:</strong> ${formatDate(product.completionDate)}</p>`;
  }
  
  // Add qualification status if available
  if (product.qualStatus) {
    html += `<p><strong>Qualification Status:</strong> ${product.qualStatus}</p>`;
  }
  
  html += `</div>
    </div>
    
    <h3>Product Roadmap</h3>
    <div id="product-roadmap"></div>
    
    <button class="back-button" onclick="goBack()">Back</button>`;
  
  detail.innerHTML = html;
  
  // Add event listeners to material filter buttons
  detail.querySelectorAll('.material-filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      // Remove active class from all buttons
      detail.querySelectorAll('.material-filter-btn').forEach(b => b.classList.remove('active'));
      // Add active class to clicked button
      this.classList.add('active');
      
      // Hide all material-specific elements
      detail.querySelectorAll('.material-specific').forEach(el => {
        el.style.display = 'none';
      });
      
      // Show elements for the selected material
      const materialId = this.getAttribute('data-filter');
      detail.querySelectorAll(`.material-specific[data-material="${materialId}"]`).forEach(el => {
        el.style.display = 'block';
      });
      
      // Update roadmap to show tasks from the selected material
      updateRoadmapMaterialTasks(product, materialId);
    });
  });
  
  // Add event listener to "View Additional Details" button
  const viewDetailsBtn = detail.querySelector('#view-material-details');
  if (viewDetailsBtn && product.materialSystems && product.materialSystems.length > 0) {
    viewDetailsBtn.addEventListener('click', function() {
      // Get the active material system
      const activeBtn = detail.querySelector('.material-filter-btn.active');
      if (activeBtn) {
        const materialId = activeBtn.getAttribute('data-filter');
        const material = roadmapData.materialSystems.find(ms => ms.id === materialId);
        if (material) {
          navStack.push('productDetailSection');
          loadMaterialDetails(material, roadmapData);
        }
      }
    });
  }
  
  // Add event listeners to supplier tiles
  detail.querySelectorAll('.supplier-tile, .supplier-link').forEach(el => {
    el.addEventListener('click', function() {
      const supplierId = this.getAttribute('data-supplier-id');
      const supplier = roadmapData.suppliers.find(s => s.id === supplierId);
      if (supplier) {
        navStack.push('productDetailSection');
        loadSupplierDetails(supplier, roadmapData);
      }
    });
  });
  
  // Show the detail view
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
  
  // Render the product roadmap
  if (product.roadmap || (product.materialSystems && product.materialSystems.length > 0)) {
    renderProductRoadmap(product, 'product-roadmap', null, roadmapData);
  }
}

// Material details function is already implemented
// Supplier details function is already implemented

function loadFundingOpportunityDetails(opp, roadmapData) {
  const detail = document.getElementById("fundingOpportunitiesDetailSection");
  
  let html = `<h2>${opp.name}</h2>
    <p><strong>Details:</strong> ${opp.details}</p>
    
    <h3>Related Entity</h3>`;
  
  // Find the related entity (could be a program, product, or material system)
  const relatedProgram = roadmapData.programs.find(p => p.id === opp.relatedEntity);
  const relatedProduct = roadmapData.products.find(p => p.id === opp.relatedEntity);
  const relatedMaterial = roadmapData.materialSystems.find(ms => ms.id === opp.relatedEntity);
  
  if (relatedProgram) {
    html += `<div class="related-entity program">
      <p><strong>Program:</strong> <span class="entity-link" data-type="program" data-id="${relatedProgram.id}">${relatedProgram.name}</span></p>
    </div>`;
  } else if (relatedProduct) {
    html += `<div class="related-entity product">
      <p><strong>Product:</strong> <span class="entity-link" data-type="product" data-id="${relatedProduct.id}">${relatedProduct.name}</span></p>
    </div>`;
  } else if (relatedMaterial) {
    html += `<div class="related-entity material">
      <p><strong>Material System:</strong> <span class="entity-link" data-type="material" data-id="${relatedMaterial.id}">${relatedMaterial.name}</span></p>
    </div>`;
  } else {
    html += `<p>No related entity found.</p>`;
  }
  
  html += `<button class="back-button" onclick="goBack()">Back</button>`;
  
  detail.innerHTML = html;
  
  // Add event listeners to entity links
  detail.querySelectorAll('.entity-link').forEach(link => {
    link.addEventListener('click', function() {
      const type = this.getAttribute('data-type');
      const id = this.getAttribute('data-id');
      
      navStack.push('fundingOpportunitiesDetailSection');
      
      if (type === 'program') {
        const program = roadmapData.programs.find(p => p.id === id);
        if (program) loadProgramDetails(program, roadmapData);
      } else if (type === 'product') {
        const product = roadmapData.products.find(p => p.id === id);
        if (product) loadProductDetails(product, roadmapData);
      } else if (type === 'material') {
        const material = roadmapData.materialSystems.find(ms => ms.id === id);
        if (material) loadMaterialDetails(material, roadmapData);
      }
    });
  });
  
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
}

module.exports = {
  loadProgramDetails,
  loadProductDetails,
  loadMaterialDetails,
  loadSupplierDetails,
  loadFundingOpportunityDetails
}; 