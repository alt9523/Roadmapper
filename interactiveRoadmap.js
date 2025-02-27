// @ts-nocheck
// interactiveRoadmap.js
// Working Version – Baseline (Phase 1) with UI Enhancements from Phase 4
//
// This script reads "roadmap.json", validates it using AJV, and generates a self-contained HTML file.
// The HTML file includes tabs for: Programs, Products, AM Material Systems, AM Suppliers, and Funding Opportunities.
// Each item appears as a clickable tile that opens a detail view. Each detail view includes a Back button
// that returns you to the previous screen using a navigation stack (navStack).
//
// UI Enhancements in this version:
// 1. A Back button returns to the previous page.
// 2. Primary color: white; Secondary color: #00269A; Tertiary color: black.
// 3. Only descriptive names are shown (no IDs).
// 4. All buttons and tiles have rounded corners.

const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');

const dataFilePath = 'roadmap.json';
const outputFilePath = 'interactive_roadmap.html';

// External repository folder (adjust as needed)
const devRepoPath = 'C:\\Users\\alt95\\OneDrive\\Documents\\Additive Manufacturing\\Roadmapper\\external';
const devRepoOutputFilePath = path.join(devRepoPath, 'interactive_roadmap.html');

// Simplified JSON schema (ensure your roadmap.json conforms to this)
const schema = {
  type: "object",
  properties: {
    programs: {
      type: "array",
      items: {
        type: "object",
        properties: { id: { type: "string" }, name: { type: "string" } },
        required: ["id", "name"]
      }
    },
    products: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          programs: { type: "array", items: { type: "string" } },
          productSupplyChain: { type: "string" }
        },
        required: ["id", "name", "programs"]
      }
    },
    materialSystems: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          qualification: { type: "string" },
          qualificationClass: { type: "string" },
          supplyChain: { type: "string" },
          standardNDT: { type: "array", items: { type: "string" } }
        },
        required: ["id", "name"]
      }
    },
    cradOpportunities: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          relatedEntity: { type: "string" },
          details: { type: "string" }
        },
        required: ["id", "name", "relatedEntity", "details"]
      }
    },
    suppliers: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          materials: { type: "array", items: { type: "string" } },
          additionalCapabilities: { type: "string" }
        },
        required: ["id", "name", "materials"]
      }
    }
  },
  required: ["programs", "products", "materialSystems", "cradOpportunities", "suppliers"]
};

const ajv = new Ajv();
const validateData = ajv.compile(schema);

/* ------------------ Navigation Helpers ------------------ */
// Declare the navigation stack so that "Back" buttons work correctly.
let navStack = [];

function goBack() {
  if (navStack.length > 0) {
    const previousView = navStack.pop();
    console.log("Going back to:", previousView);
    
    // Hide all views first
    document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
    document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
    
    // Show the previous view
    const viewElement = document.getElementById(previousView);
    if (viewElement) {
      viewElement.classList.add("active");
    } else {
      // Fallback to programs view if something goes wrong
      document.getElementById("programsView").classList.add("active");
    }
  } else {
    // If navStack is empty, go to programs view
    document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
    document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
    document.getElementById("programsView").classList.add("active");
  }
}

function showMainView(viewId) {
  // Hide all main views and detail views; then show the specified main view (default to Programs view).
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  if (viewId) {
    document.getElementById(viewId).classList.add("active");
  } else {
    document.getElementById("programsView").classList.add("active");
  }
}

/* ------------------ Detail View Functions ------------------ */
function loadProductDetails(product) {
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
    
    // Remove the "All" button and just add material system buttons
    product.materialSystems.forEach((msId, index) => {
      const material = roadmapData.materialSystems.find(ms => ms.id === msId);
      if (material) {
        // Make the first material system active by default
        const isActive = index === 0 ? 'active' : '';
        html += `<span class="material-filter-btn ${isActive}" data-filter="${material.id}">${material.name}</span>`;
      }
    });
    
    html += `</div>`;
    
    // Add a single "View Additional Details" button instead of individual buttons
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
      
      <!-- Second quad box: Design -->
      <div class="quad-box">
        <h3>Design</h3>
        <div class="design-section">`;
  
  // Add design tools
  if (product.designTools && product.designTools.length > 0) {
    html += `
      <div class="design-tools">
        <h4>Design Tools</h4>
        <ul>`;
    
    product.designTools.forEach(tool => {
      html += `<li>${tool}</li>`;
    });
    
    html += `</ul>
      </div>`;
  } else {
    html += `<p>No specific design tools defined.</p>`;
  }
  
  // Add documentation
  if (product.documentation && product.documentation.length > 0) {
    html += `
      <div class="documentation">
        <h4>Documentation</h4>
        <ul>`;
    
    product.documentation.forEach(doc => {
      html += `<li>${doc}</li>`;
    });
    
    html += `</ul>
      </div>`;
  }
  
  html += `</div>
      </div>
      
      <!-- Third quad box: Manufacturing -->
      <div class="quad-box">
        <h3>Manufacturing</h3>
        <div class="manufacturing-section">`;
  
  // Display qualified machines from the selected material system
  if (product.materialSystems && product.materialSystems.length > 0) {
    product.materialSystems.forEach((msId, index) => {
      const material = roadmapData.materialSystems.find(ms => ms.id === msId);
      if (material && material.qualifiedMachines && material.qualifiedMachines.length > 0) {
        // Only show the first material system's machines by default
        const displayStyle = index === 0 ? 'block' : 'none';
        html += `
          <div class="qualified-machines material-specific" data-material="${material.id}" style="display: ${displayStyle};">
            <h4>${material.name} Qualified Machines</h4>
            <ul>`;
        
        material.qualifiedMachines.forEach(machine => {
          html += `<li>${machine}</li>`;
        });
        
        html += `</ul>
          </div>`;
      }
    });
  }
  
  // Add printing suppliers as clickable tiles
  if (product.relevantSuppliers && product.relevantSuppliers.length > 0) {
    html += `
      <div class="printing-suppliers">
        <h4>Printing Suppliers</h4>
        <div class="supplier-tiles">`;
    
    product.relevantSuppliers.forEach(supplierId => {
      const supplier = roadmapData.suppliers.find(s => s.id === supplierId);
      if (supplier) {
        html += `<div class="supplier-tile" data-supplier-id="${supplier.id}">${supplier.name}</div>`;
      }
    });
    
    html += `</div>
      </div>`;
  }
  
  // Add post-processing suppliers
  if (product.postProcessingSuppliers && product.postProcessingSuppliers.length > 0) {
    html += `
      <div class="post-processing-suppliers">
        <h4>Post Processing Suppliers</h4>
        <table class="post-processing-suppliers-table">
          <tr>
            <th>Process</th>
            <th>Supplier</th>
          </tr>`;
    
    product.postProcessingSuppliers.forEach(item => {
      const supplier = roadmapData.suppliers.find(s => s.id === item.supplier);
      if (supplier) {
        html += `
          <tr>
            <td>${item.process}</td>
            <td><span class="supplier-link" data-supplier-id="${supplier.id}">${supplier.name}</span></td>
          </tr>`;
      }
    });
    
    html += `</table>
      </div>`;
  }
  
  html += `</div>
      </div>
      
      <!-- Fourth quad box: Quality -->
      <div class="quad-box">
        <h3>Quality</h3>
        <div class="quality-section">`;
  
  // Add standard NDT from material systems
  if (product.materialSystems && product.materialSystems.length > 0) {
    product.materialSystems.forEach((msId, index) => {
      const material = roadmapData.materialSystems.find(ms => ms.id === msId);
      if (material && material.standardNDT && material.standardNDT.length > 0) {
        // Only show the first material system's NDT by default
        const displayStyle = index === 0 ? 'block' : 'none';
        html += `
          <div class="standard-ndt material-specific" data-material="${material.id}" style="display: ${displayStyle};">
            <h4>${material.name} Standard NDE/NDI/NDT</h4>
            <ul>`;
        
        material.standardNDT.forEach(ndt => {
          html += `<li>${ndt}</li>`;
        });
        
        html += `</ul>
          </div>`;
      }
    });
  }
  
  // Add product specific NDT
  if (product.specialNDT && product.specialNDT.length > 0) {
    html += `
      <div class="special-ndt">
        <h4>Product Specific NDE/NDI/NDT</h4>
        <ul>`;
    
    product.specialNDT.forEach(ndt => {
      html += `<li>${ndt}</li>`;
    });
    
    html += `</ul>
      </div>`;
  }
  
  // Add part acceptance
  if (product.partAcceptance && product.partAcceptance.length > 0) {
    html += `
      <div class="part-acceptance">
        <h4>Part Acceptance</h4>
        <ul>`;
    
    product.partAcceptance.forEach(acceptance => {
      html += `<li>${acceptance}</li>`;
    });
    
    html += `</ul>
      </div>`;
  }
  
  html += `</div>
      </div>
    </div>
    
    <h3>Technical Roadmap</h3>
    <div id="product-roadmap"></div>
    
    <button class="back-button" onclick="goBack()">Back</button>`;
  
  // Set the HTML content
  detail.innerHTML = html;
  
  // Add click event listeners to material filter buttons
  detail.querySelectorAll('.material-filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const filter = this.getAttribute('data-filter');
      
      // Update active button
      detail.querySelectorAll('.material-filter-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      // Show/hide material-specific content
      detail.querySelectorAll('.material-specific').forEach(el => {
        el.style.display = el.getAttribute('data-material') === filter ? 'block' : 'none';
      });
      
      // Update the roadmap to show tasks from the selected material system
      updateRoadmapMaterialTasks(product, filter);
    });
  });
  
  // Add click event listener to the single material details button
  const viewDetailsBtn = detail.querySelector('#view-material-details');
  if (viewDetailsBtn) {
    viewDetailsBtn.addEventListener('click', function() {
      // Get the currently active material filter
      const activeFilter = detail.querySelector('.material-filter-btn.active');
      if (activeFilter) {
        const materialId = activeFilter.getAttribute('data-filter');
        const material = roadmapData.materialSystems.find(ms => ms.id === materialId);
        if (material) {
          navStack.push('productDetailSection');
          loadMaterialDetails(material);
        }
      }
    });
  }
  
  // Add event listeners for supplier tiles and links
  detail.querySelectorAll('.supplier-tile, .supplier-link').forEach(element => {
    element.addEventListener('click', function() {
      const supplierId = this.getAttribute('data-supplier-id');
      const supplier = roadmapData.suppliers.find(s => s.id === supplierId);
      if (supplier) {
        navStack.push('productDetailSection');
        loadSupplierDetails(supplier);
      }
    });
  });
  
  // Render the roadmap
  renderProductRoadmap(product, "product-roadmap");
  
  // Hide all main and detail views before showing this detail view
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
  
  // After rendering the product roadmap, make sure to show the first material system's tasks
  renderProductRoadmap(product, 'product-roadmap');
  
  // Add click event listeners to material filter buttons
  detail.querySelectorAll('.material-filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const filter = this.getAttribute('data-filter');
      
      // Update active button
      detail.querySelectorAll('.material-filter-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      // Show/hide material-specific content
      detail.querySelectorAll('.material-specific').forEach(el => {
        el.style.display = el.getAttribute('data-material') === filter ? 'block' : 'none';
      });
      
      // Update the roadmap to show tasks from the selected material system
      updateRoadmapMaterialTasks(product, filter);
    });
  });
  
  // Trigger the first material filter button click to ensure M&P tasks are shown
  if (product.materialSystems && product.materialSystems.length > 0) {
    const firstMaterialBtn = detail.querySelector('.material-filter-btn');
    if (firstMaterialBtn) {
      firstMaterialBtn.click();
    }
  }
}

// Helper function to get color based on status
function getStatusColor(status) {
  const statusLower = (status || "").toLowerCase();
  if (statusLower === "complete") return "#4CAF50";
  if (statusLower === "in progress") return "#2196F3";
  return "#9E9E9E"; // Default for planned or other statuses
}

// Helper function to format dates
function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString();
}

function loadMaterialDetails(material) {
  const detail = document.getElementById("materialDetailSection");
  
  let html = `<h2>${material.name}</h2>
    <div class="material-details-grid">
      <div class="material-details-section">
        <h3>Overview</h3>
        <p><strong>Process:</strong> ${material.process || 'N/A'}</p>
        <p><strong>Material:</strong> ${material.material || 'N/A'}</p>`;
  
  // Determine qualification status text
  let qualificationText = material.qualificationClass || 'N/A';
  if (material.qualification !== 'Qualified') {
    qualificationText += ' (In Development)';
  }
  
  html += `<p><strong>Qualification:</strong> ${qualificationText}</p>
        <p><strong>Supply Chain:</strong> ${material.supplyChain || 'N/A'}</p>
      </div>
      
      <div class="material-details-section">
        <h3>Properties</h3>`;
  
  if (material.properties) {
    html += `<ul>`;
    Object.entries(material.properties).forEach(([key, value]) => {
      html += `<li><strong>${key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}:</strong> ${value}</li>`;
    });
    html += `</ul>`;
  } else {
    html += `<p>No property data available.</p>`;
  }
  
  html += `</div>
      
      <div class="material-details-section">
        <h3>Processing Parameters</h3>`;
  
  if (material.processingParameters) {
    html += `<ul>`;
    Object.entries(material.processingParameters).forEach(([key, value]) => {
      html += `<li><strong>${key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}:</strong> ${value}</li>`;
    });
    html += `</ul>`;
  } else {
    html += `<p>No processing parameter data available.</p>`;
  }
  
  html += `</div>
      
      <div class="material-details-section">
        <h3>Post Processing</h3>`;
  
  if (material.postProcessing && material.postProcessing.length > 0) {
    html += `<ul>`;
    material.postProcessing.forEach(process => {
      html += `<li>${process}</li>`;
    });
    html += `</ul>`;
  } else {
    html += `<p>No post-processing data available.</p>`;
  }
  
  html += `</div>
      
      <div class="material-details-section">
        <h3>Qualified Machines</h3>`;
  
  if (material.qualifiedMachines && material.qualifiedMachines.length > 0) {
    html += `<ul>`;
    material.qualifiedMachines.forEach(machine => {
      html += `<li>${machine}</li>`;
    });
    html += `</ul>`;
  } else {
    html += `<p>No qualified machines available.</p>`;
  }
  
  html += `</div>
      
      <div class="material-details-section">
        <h3>Standard NDE/NDI/NDT</h3>`;
  
  if (material.standardNDT && material.standardNDT.length > 0) {
    html += `<ul>`;
    material.standardNDT.forEach(ndt => {
      html += `<li>${ndt}</li>`;
    });
    html += `</ul>`;
  } else {
    html += `<p>No standard NDT data available.</p>`;
  }
  
  html += `</div>`;
  
  html += `</div>
    
    <h3>Material Roadmap</h3>
    <div class="material-roadmap">`;
  
  if (material.roadmap && material.roadmap.length > 0) {
    material.roadmap.forEach(item => {
      html += `
        <div class="roadmap-item" style="background-color: ${getStatusColor(item.status)}">
          <div class="item-name">${item.task}</div>
          <div class="item-dates">${formatDate(item.start)} - ${formatDate(item.end)}</div>
          <div class="item-status">${item.status}</div>
        </div>`;
    });
  } else {
    html += `<p>No roadmap data available.</p>`;
  }
  
  html += `</div>
    
    <h3>Milestones</h3>
    <div class="material-milestones">`;
  
  if (material.milestones && material.milestones.length > 0) {
    material.milestones.forEach(milestone => {
      html += `
        <div class="milestone">
          <div class="milestone-name">${milestone.name}</div>
          <div class="milestone-date">${formatDate(milestone.date)}</div>
          <div class="milestone-description">${milestone.description}</div>
        </div>`;
    });
  } else {
    html += `<p>No milestone data available.</p>`;
  }
  
  html += `</div>
    
    <button class="back-button" onclick="goBack()">Back</button>`;
  
  detail.innerHTML = html;
  
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
}

function loadSupplierDetails(supplier) {
  const detail = document.getElementById("supplierDetailSection");
  detail.innerHTML = `<h2>${supplier.name}</h2>
    <p><strong>Additional Capabilities:</strong> ${supplier.additionalCapabilities || "N/A"}</p>
    <button class="back-button" onclick="goBack()">Back</button>`;
  
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
}

function loadFundingOpportunityDetails(opp) {
  const detail = document.getElementById("fundingOpportunitiesDetailSection");
  detail.innerHTML = `<h2>${opp.name}</h2>
    <p>${opp.details}</p>
    <button class="back-button" onclick="goBack()">Back</button>`;
  
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
}

function loadProgramDetails(program) {
  const detail = document.getElementById("programDetailSection");
  detail.innerHTML = `
    <h2>${program.name}</h2>
    <p><strong>Customer Name:</strong> ${program.customerName || "N/A"}</p>
    <p><strong>Division:</strong> ${program.division || "N/A"}</p>
    <p><strong>Mission Class:</strong> ${program.missionClass || "N/A"}</p>
    <p><strong>Need Date:</strong> ${program.needDate || "N/A"}</p>
    <h3>Products of Interest</h3>
    <div id="programProductsContainer" class="tile-container"></div>
    <button class="back-button" onclick="goBack()">Back</button>
  `;

  // Render clickable product tiles that load product details
  const products = roadmapData.products.filter(p => p.programs.includes(program.id));
  const container = detail.querySelector("#programProductsContainer");
  if (products.length > 0) {
    products.forEach(product => {
      const tile = document.createElement("div");
      tile.className = "tile";
      tile.innerHTML = `
        <strong>${product.name}</strong><br>
        <small>Qual Status: ${product.qualStatus || "N/A"}</small><br>
        <small>Completion Date: ${product.completionDate || "N/A"}</small><br>
        <small>Implementation Status: ${product.implementationStatus || "N/A"}</small>
      `;
      tile.onclick = () => {
        navStack.push("programDetailSection");
        loadProductDetails(product);
      };
      container.appendChild(tile);
    });
  } else {
    container.innerHTML = "<p>No products of interest available.</p>";
  }

  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
}


/* ---------- Corrected renderPrograms Function ---------- */
function renderPrograms() {
  const container = document.getElementById("programsView");
  container.innerHTML = "";

  // Group programs by division if they have one
  const hasDivision = roadmapData.programs.some(prog => prog.division);
  if (hasDivision) {
    // Create a dictionary keyed by division name
    const groups = {};
    roadmapData.programs.forEach(prog => {
      const divName = prog.division || "Unassigned Division";
      if (!groups[divName]) {
        groups[divName] = [];
      }
      groups[divName].push(prog);
    });

    // Render each division, then each program
    for (const division in groups) {
      // Division "header" tile
      const divisionTile = document.createElement("div");
      divisionTile.className = "tile";
      divisionTile.style.backgroundColor = "#eee"; 
      divisionTile.style.marginBottom = "10px";
      divisionTile.innerHTML = `<h2>${division}</h2>`;

      // Container for that division's programs
      const programsContainer = document.createElement("div");
      programsContainer.style.marginLeft = "20px";

      groups[division].forEach(program => {
        const programTile = document.createElement("div");
        programTile.className = "tile";
        programTile.innerHTML = `<h3>${program.name}</h3>`;
        programTile.style.marginBottom = "5px";
        programTile.onclick = event => {
          event.stopPropagation(); // don't trigger the division tile click
          console.log("Program tile clicked:", program);
          navStack.push("programsView");
          loadProgramDetails(program); // <--- calls the function
        };
        programsContainer.appendChild(programTile);
      });

      divisionTile.appendChild(programsContainer);
      container.appendChild(divisionTile);
    }
  } else {
    // If no division data, list programs normally
    roadmapData.programs.forEach(program => {
      const tile = document.createElement("div");
      tile.className = "tile";
      tile.innerHTML = `<h2>${program.name}</h2>`;
      tile.onclick = () => {
        console.log("Program tile clicked:", program);
        navStack.push("programsView");
        loadProgramDetails(program);
      };
      container.appendChild(tile);
    });
  }
}



/* ------------------ Rendering Functions for Main Views ------------------ */


function renderProducts() {
  const container = document.getElementById("productsView");
  if (!container) return;
  
  let html = `<h2>Products</h2>
    <div class="tiles-container">`;
  
  roadmapData.products.forEach(product => {
    html += `
      <div class="tile" data-product-id="${product.id}">
        <div class="tile-name">${product.name}</div>
      </div>`;
  });
  
  html += `</div>`;
  container.innerHTML = html;
  
  // Add event listeners to product tiles
  container.querySelectorAll(".tile").forEach(tile => {
    tile.addEventListener("click", function() {
      const productId = this.getAttribute("data-product-id");
      const product = roadmapData.products.find(p => p.id === productId);
      if (product) {
        loadProductDetails(product);
      }
    });
  });
}

function renderAMMaterialSystems() {
  const container = document.getElementById("amMaterialSystemsView");
  container.innerHTML = "";
  roadmapData.materialSystems.forEach(ms => {
    const tile = document.createElement("div");
    tile.className = "tile";
    tile.textContent = ms.name;
    tile.onclick = () => {
      navStack.push("amMaterialSystemsView");
      loadMaterialDetails(ms);
    };
    container.appendChild(tile);
  });
}

function renderAMSuppliers() {
  const container = document.getElementById("amSuppliersView");
  container.innerHTML = "";
  roadmapData.suppliers.forEach(sup => {
    const tile = document.createElement("div");
    tile.className = "tile";
    tile.textContent = sup.name;
    tile.onclick = () => {
      navStack.push("amSuppliersView");
      loadSupplierDetails(sup);
    };
    container.appendChild(tile);
  });
}

function renderFundingOpportunities() {
  const container = document.getElementById("fundingOpportunitiesView");
  container.innerHTML = "";
  roadmapData.cradOpportunities.forEach(opp => {
    const tile = document.createElement("div");
    tile.className = "tile";
    tile.textContent = opp.name;
    tile.onclick = () => {
      navStack.push("fundingOpportunitiesView");
      loadFundingOpportunityDetails(opp);
    };
    container.appendChild(tile);
  });
}

/* ------------------ HTML Generation ------------------ */
function generateHtmlContent(data) {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Interactive AM Roadmap - Working Version</title>
  <style>
    /* Colors: Primary = white, Secondary = #00269A, Tertiary = black */
    body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: white; color: black; }
    header { background-color: #00269A; color: white; padding: 15px; text-align: center; }
    .container { padding: 20px; }
    .tabs { display: flex; background-color: #ddd; margin-bottom: 10px; }
    .tab-button { padding: 10px; flex: 1; cursor: pointer; text-align: center; border-radius: 8px; border: none; }
    .tab-button.active { background-color: #00269A; color: white; font-weight: bold; }
    .view { display: none; }
    .view.active { display: block; }
    .detail-view { display: none; }
    .detail-view.active { display: block; }
    .tile {
      background: white;
      border: 1px solid #ccc;
      padding: 15px;
      margin: 10px;
      cursor: pointer;
      display: inline-block;
      border-radius: 8px;
      transition: background-color 0.2s, transform 0.1s;
      min-width: 200px;
      text-align: center;
    }
    .tile:hover {
      background-color: #f0f0f0;
      transform: translateY(-2px);
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tiles-container {
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-start;
      margin-top: 20px;
    }
    .tile-name {
      font-weight: bold;
      font-size: 16px;
    }
    .back-button { padding: 8px 16px; margin-top: 10px; border-radius: 8px; background-color: #00269A; color: white; border: none; cursor: pointer; }
    .material-links { margin-bottom: 20px; }
    .material-link { display: inline-block; background-color: #00269A; color: white; padding: 5px 10px; margin: 0 5px 5px 0; border-radius: 5px; cursor: pointer; }
    .roadmap-swimlanes { display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; }
    .swimlane { border: 1px solid #ddd; border-radius: 8px; padding: 10px; }
    .swimlane h4 { margin-top: 0; padding-bottom: 5px; border-bottom: 1px solid #eee; }
    .swimlane-items { min-height: 50px; }
    .roadmap-item { background-color: #f5f5f5; border-radius: 5px; padding: 8px; margin-bottom: 5px; }
    .item-name { font-weight: bold; }
    .item-dates, .item-status { font-size: 0.9em; color: #555; }
    .quad-layout {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      grid-template-rows: repeat(2, auto);
      gap: 20px;
      margin-bottom: 30px;
    }
    .quad-box {
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 15px;
      background-color: #f9f9f9;
    }
    .quad-box h3 {
      margin-top: 0;
      color: #00269A;
      border-bottom: 1px solid #ddd;
      padding-bottom: 8px;
      margin-bottom: 15px;
    }
    .quad-box ul {
      margin-top: 5px;
    }
    .material-filter {
      margin-bottom: 15px;
    }
    .material-filter-btn, .material-details-btn {
      display: inline-block;
      background-color: #ddd;
      color: #333;
      padding: 5px 10px;
      margin: 0 5px 5px 0;
      border-radius: 5px;
      cursor: pointer;
    }
    .material-filter-btn.active {
      background-color: #00269A;
      color: white;
    }
    .material-details-btn {
      background-color: #000;
      color: white;
      margin-top: 10px;
      display: inline-block;
      padding: 8px 12px;
      border-radius: 5px;
      cursor: pointer;
    }
    .material-specific {
      display: none;
    }
    .material-details-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin-bottom: 20px;
    }
    .material-details-section {
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 15px;
      background-color: #f9f9f9;
    }
    .material-details-section h3 {
      margin-top: 0;
      color: #00269A;
      border-bottom: 1px solid #ddd;
      padding-bottom: 8px;
      margin-bottom: 15px;
    }
    .material-roadmap, .material-milestones {
      margin-bottom: 20px;
    }
    .milestone {
      background-color: #f0f8ff;
      border-left: 4px solid #00269A;
      padding: 10px;
      margin-bottom: 10px;
    }
    .milestone-name {
      font-weight: bold;
    }
    .milestone-date {
      color: #666;
      font-size: 0.9em;
    }
    .supplier-tiles {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 10px;
    }
    .supplier-tile {
      background-color: #f0f0f0;
      border: 1px solid #ddd;
      border-radius: 5px;
      padding: 8px 12px;
      cursor: pointer;
      transition: background-color 0.2s;
    }
    .supplier-tile:hover {
      background-color: #e0e0e0;
    }
    .post-processing-suppliers-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }
    .post-processing-suppliers-table th, 
    .post-processing-suppliers-table td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }
    .post-processing-suppliers-table th {
      background-color: #f5f5f5;
    }
    .supplier-link {
      color: #00269A;
      cursor: pointer;
      text-decoration: underline;
    }
    .supplier-link:hover {
      color: #001a6d;
    }
    .roadmap-container {
      margin-top: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
      overflow: hidden;
      background-color: #fff;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .roadmap-container.dark-theme {
      background-color: #1a1a1a;
      color: white;
      border-color: #444;
    }
    .roadmap-timeline-controls {
      padding: 10px;
      background-color: #f5f5f5;
      border-bottom: 1px solid #ddd;
      display: flex;
      align-items: center;
    }
    .dark-theme .roadmap-timeline-controls {
      background-color: #333;
      border-color: #444;
      color: white;
    }
    .start-date-picker {
      margin-left: 10px;
      padding: 5px;
      border-radius: 4px;
      border: 1px solid #ccc;
    }
    .roadmap-timeline {
      position: relative;
      overflow-x: auto;
    }
    .roadmap-header {
      display: flex;
      border-bottom: 1px solid #ddd;
      background-color: #f9f9f9;
    }
    .dark-theme .roadmap-header {
      background-color: #333;
      border-color: #444;
    }
    .roadmap-header-lane {
      flex: 0 0 150px;
      padding: 10px;
      font-weight: bold;
      border-right: 1px solid #ddd;
    }
    .dark-theme .roadmap-header-lane {
      border-color: #444;
    }
    .roadmap-header-quarter {
      flex: 0 0 100px;
      padding: 10px;
      text-align: center;
      font-weight: bold;
      border-right: 1px solid #eee;
    }
    .dark-theme .roadmap-header-quarter {
      border-color: #444;
    }
    .roadmap-row {
      display: flex;
      border-bottom: 1px solid #ddd;
      min-height: 60px;
    }
    .dark-theme .roadmap-row {
      border-color: #444;
    }
    .roadmap-lane-title {
      flex: 0 0 150px;
      padding: 10px;
      font-weight: bold;
      background-color: #f5f5f5;
      border-right: 1px solid #ddd;
      display: flex;
      align-items: center;
    }
    .dark-theme .roadmap-lane-title {
      background-color: #333;
      border-color: #444;
    }
    .roadmap-lane-content {
      flex: 1;
      position: relative;
      min-width: 2000px;
    }
    .roadmap-task {
      position: absolute;
      height: 25px;
      border-radius: 4px;
      padding: 4px;
      overflow: hidden;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      border: 1px solid rgba(255,255,255,0.2);
      cursor: pointer;
      transition: transform 0.1s, box-shadow 0.1s;
    }
    .roadmap-task:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.3);
      z-index: 10;
    }
    .roadmap-task.complete {
      background-color: #4CAF50;
      border-color: #81C784;
    }
    .roadmap-task.in-progress {
      background-color: #42A5F5;
      border-color: #90CAF9;
    }
    .roadmap-task.in-progress.funding-sector-irad {
      background-color: #AB47BC;
      border-color: #CE93D8;
    }
    .roadmap-task.in-progress.funding-division-irad {
      background-color: #FFA726;
      border-color: #FFCC80;
    }
    .roadmap-task.in-progress.funding-crad {
      background-color: #EC407A;
      border-color: #F48FB1;
    }
    .roadmap-task.planned {
      background-color: #BDBDBD;
      border-color: #E0E0E0;
      color: #212121;
    }
    .task-label {
      font-size: 12px;
      font-weight: bold;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    .milestone-row {
      background-color: #f0f8ff;
      border-bottom: 2px solid #00269A;
    }
    .dark-theme .milestone-row {
      background-color: #1a2a3a;
      border-color: #00269A;
    }
    .programs-row {
      background-color: #f0f0ff;
      border-bottom: 2px solid #00269A;
    }
    .dark-theme .programs-row {
      background-color: #1a1a3a;
      border-color: #00269A;
    }
    .roadmap-milestone {
      position: absolute;
      top: 5px;
      transform: translateX(-50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 20px;
    }
    .milestone-marker {
      width: 20px;
      height: 20px;
      background-color: #4a89ff;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .dark-theme .milestone-marker {
      border-color: #333;
    }
    .milestone-label {
      margin-top: 5px;
      font-size: 12px;
      font-weight: bold;
      white-space: nowrap;
      transform: rotate(-45deg);
      transform-origin: top left;
    }
    .program-marker {
      position: absolute;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .program-marker-point {
      width: 16px;
      height: 16px;
      background-color: #ff5722;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .dark-theme .program-marker-point {
      border-color: #333;
    }
    .program-marker-label {
      margin-top: 5px;
      font-size: 12px;
      font-weight: bold;
      white-space: nowrap;
      /* Remove the transform that was rotating the text */
      /* transform: rotate(-45deg); */
      /* transform-origin: top left; */
    }
    .roadmap-key {
      margin-top: 20px;
      padding: 15px;
      background-color: #f9f9f9;
      border-radius: 8px;
      border: 1px solid #ddd;
    }
    .dark-theme .roadmap-key {
      background-color: #333;
      border-color: #444;
    }
    .roadmap-key h4 {
      margin-top: 0;
      margin-bottom: 10px;
    }
    .key-items {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
    }
    .key-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .key-color {
      width: 20px;
      height: 20px;
      border-radius: 4px;
    }
    .key-color.planned {
      background-color: #BDBDBD;
      border: 1px solid #E0E0E0;
    }
    .key-color.in-progress {
      background-color: #42A5F5;
      border: 1px solid #90CAF9;
    }
    .key-color.in-progress.funding-sector-irad {
      background-color: #AB47BC;
      border: 1px solid #CE93D8;
    }
    .key-color.in-progress.funding-division-irad {
      background-color: #FFA726;
      border: 1px solid #FFCC80;
    }
    .key-color.in-progress.funding-crad {
      background-color: #EC407A;
      border: 1px solid #F48FB1;
    }
    .key-color.complete {
      background-color: #4CAF50;
      border: 1px solid #81C784;
    }
    .key-label {
      font-size: 14px;
      color: #333;
    }
    .dark-theme .key-label {
      color: #f0f0f0;
    }
    .roadmap-source-note {
      margin-top: 10px;
      font-size: 12px;
      font-style: italic;
      color: #666;
    }
    .dark-theme .roadmap-source-note {
      color: #aaa;
    }
    
    /* Task Detail Styles */
    .task-details-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 15px;
      margin: 20px 0;
    }
    
    .task-detail-item {
      background-color: #f5f5f5;
      padding: 15px;
      border-radius: 5px;
      border-left: 3px solid #00269A;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .dark-theme .task-detail-item {
      background-color: #333;
      border-left-color: #4a89ff;
      color: #f0f0f0;
    }
    
    /* Improved roadmap task styling */
    .roadmap-task {
      position: absolute;
      border-radius: 4px;
      padding: 4px 8px;
      overflow: hidden;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      border: 1px solid rgba(255,255,255,0.2);
      cursor: pointer;
      transition: transform 0.1s, box-shadow 0.1s, opacity 0.2s;
    }
    
    .roadmap-task:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.3);
      z-index: 100;
      opacity: 0.9;
    }
    
    .roadmap-task:active {
      transform: translateY(0);
      box-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .task-label {
      font-size: 12px;
      font-weight: bold;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
      color: white;
    }
    
    .roadmap-task.planned .task-label {
      color: #212121;
      text-shadow: none;
    }
  </style>
</head>
<body>
  <header><h1>Interactive AM Roadmap</h1></header>
  <div class="container">
    <div class="tabs">
      <button id="programsTab" class="tab-button active">Programs</button>
      <button id="productsTab" class="tab-button">Products</button>
      <button id="amMaterialSystemsTab" class="tab-button">AM Material Systems</button>
      <button id="amSuppliersTab" class="tab-button">AM Suppliers</button>
      <button id="fundingOpportunitiesTab" class="tab-button">Funding Opportunities</button>
    </div>
    <div id="programsView" class="view main-view active">
      <h2>Programs</h2>
      <div id="programsContainer"></div>
    </div>
    <div id="productsView" class="view main-view">
      <h2>Products</h2>
      <div id="productsContainer"></div>
    </div>
    <div id="amMaterialSystemsView" class="view main-view">
      <h2>AM Material Systems</h2>
      <div id="amMaterialSystemsContainer"></div>
    </div>
    <div id="amSuppliersView" class="view main-view">
      <h2>AM Suppliers</h2>
      <div id="amSuppliersContainer"></div>
    </div>
    <div id="fundingOpportunitiesView" class="view main-view">
      <h2>Funding Opportunities</h2>
      <div id="fundingOpportunitiesContainer"></div>
    </div>
    
    <!-- Detail Views -->
    <div id="programDetailSection" class="detail-view"></div>
    <div id="productDetailSection" class="detail-view"></div>
    <div id="materialDetailSection" class="detail-view"></div>
    <div id="supplierDetailSection" class="detail-view"></div>
    <div id="fundingOpportunitiesDetailSection" class="detail-view"></div>
    <div id="taskDetailSection" class="detail-view"></div>
  </div>
  <script>
    // Declare navStack so that the Back button works properly.
    let navStack = [];
    
    const roadmapData = ${JSON.stringify(data, null, 2)};
    
    ${loadProgramDetails.toString()}
    ${renderPrograms.toString()}
    ${renderProducts.toString()}
    ${renderAMMaterialSystems.toString()}
    ${renderAMSuppliers.toString()}
    ${renderFundingOpportunities.toString()}
    ${goBack.toString()}
    ${showMainView.toString()}
    ${loadProductDetails.toString()}
    ${loadMaterialDetails.toString()}
    ${loadSupplierDetails.toString()}
    ${loadFundingOpportunityDetails.toString()}
    ${getStatusColor.toString()}
    ${formatDate.toString()}
    ${formatDateForInput.toString()}
    ${renderProductRoadmap.toString()}
    ${adjustRowHeights.toString()}
    ${loadTaskDetails.toString()}
    ${createTaskDetailSection.toString()}
    ${updateRoadmapMaterialTasks.toString()}
    
    document.getElementById("programsTab").addEventListener("click", function() {
      navStack = []; // Reset navStack for new view
      document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      showMainView("programsView");
      renderPrograms();
    });
    document.getElementById("productsTab").addEventListener("click", function() {
      navStack = []; // Optionally reset the navigation stack on a tab switch
      document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      showMainView("productsView");
      renderProducts();
    });
    document.getElementById("amMaterialSystemsTab").addEventListener("click", function() {
      navStack = []; // Optionally reset the navigation stack on a tab switch
      document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      showMainView("amMaterialSystemsView");
      renderAMMaterialSystems();
    });
    document.getElementById("amSuppliersTab").addEventListener("click", function() {
      navStack = []; // Optionally reset the navigation stack on a tab switch
      document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      showMainView("amSuppliersView");
      renderAMSuppliers();
    });
    document.getElementById("fundingOpportunitiesTab").addEventListener("click", function() {
      navStack = []; // Optionally reset the navigation stack on a tab switch
      document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      showMainView("fundingOpportunitiesView");
      renderFundingOpportunities();
    });
    
    function showMainView(viewId) {
      // Hide all main and detail views, then show the specified main view
      document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
      document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
      if (viewId) {
        document.getElementById(viewId).classList.add("active");
      } else {
        document.getElementById("programsView").classList.add("active");
      }
    }

    // Initialize with Programs view
    renderPrograms();
  </script>
</body>
</html>`;
}

function buildHTML() {
  try {
    const data = JSON.parse(fs.readFileSync(dataFilePath, "utf8"));
    const valid = validateData(data);
    if (!valid) {
      console.error("Data validation error: " + JSON.stringify(validateData.errors, null, 2));
      return;
    }
    console.log("Data validation successful.");
    const htmlContent = generateHtmlContent(data);
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

// Fix the loadTaskDetails function to properly handle navigation
function loadTaskDetails(task, source, materialId) {
  // Create a new detail section for task details
  const detail = document.getElementById("taskDetailSection") || createTaskDetailSection();
  
  // Store the current view in navigation stack BEFORE changing views
  // This is the key fix - we need to store the product detail section ID
  navStack.push("productDetailSection");
  
  // Determine the source text and additional info based on where the task came from
  let sourceText = '';
  
  if (source === 'material') {
    const material = roadmapData.materialSystems.find(ms => ms.id === materialId);
    sourceText = `<p><strong>Source:</strong> Material System - ${material ? material.name : materialId}</p>`;
  } else {
    sourceText = `<p><strong>Source:</strong> Product Roadmap</p>`;
  }
  
  // Build the HTML content
  let html = `
    <h2>Task Details: ${task.task}</h2>
    ${sourceText}
    <div class="task-details-grid">
      <div class="task-detail-item">
        <strong>Start Date:</strong> ${formatDate(task.start)}
      </div>
      <div class="task-detail-item">
        <strong>End Date:</strong> ${formatDate(task.end)}
      </div>
      <div class="task-detail-item">
        <strong>Status:</strong> ${task.status}
      </div>`;
  
  // Add funding type if available
  if (task.fundingType) {
    html += `
      <div class="task-detail-item">
        <strong>Funding Type:</strong> ${task.fundingType}
      </div>`;
  }
  
  // Add lane if available
  if (task.lane) {
    html += `
      <div class="task-detail-item">
        <strong>Category:</strong> ${task.lane}
      </div>`;
  }
  
  // Add any additional fields that might be in the task object
  for (const [key, value] of Object.entries(task)) {
    // Skip fields we've already displayed
    if (['task', 'start', 'end', 'status', 'fundingType', 'lane'].includes(key)) continue;
    
    html += `
      <div class="task-detail-item">
        <strong>${key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}:</strong> ${value}
      </div>`;
  }
  
  html += `</div>
    <button class="back-button" onclick="goBack()">Back</button>`;
  
  // Set the HTML content
  detail.innerHTML = html;
  
  // Hide all main and detail views before showing this detail view
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
}

// Fix the goBack function to properly handle navigation
function goBack() {
  if (navStack.length > 0) {
    const previousView = navStack.pop();
    console.log("Going back to:", previousView);
    
    // Hide all views first
    document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
    document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
    
    // Show the previous view
    const viewElement = document.getElementById(previousView);
    if (viewElement) {
      viewElement.classList.add("active");
    } else {
      // Fallback to programs view if something goes wrong
      document.getElementById("programsView").classList.add("active");
    }
  } else {
    // If navStack is empty, go to programs view
    document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
    document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
    document.getElementById("programsView").classList.add("active");
  }
}

// Helper function to create the task detail section if it doesn't exist
function createTaskDetailSection() {
  const detail = document.createElement('div');
  detail.id = 'taskDetailSection';
  detail.className = 'detail-view';
  document.querySelector('.container').appendChild(detail);
  return detail;
}

// Improved function to adjust row heights based on content
function adjustRowHeights(container) {
  const rows = container.querySelectorAll('.roadmap-row');
  
  rows.forEach(row => {
    const content = row.querySelector('.roadmap-lane-content');
    const items = content.querySelectorAll('.roadmap-task, .roadmap-milestone, .program-marker');
    
    if (items.length > 0) {
      // Create a map to track vertical positions
      const verticalPositions = [];
      
      // First pass: collect all vertical positions and heights
      items.forEach(item => {
        const top = parseInt(item.style.top || '0', 10);
        const height = item.offsetHeight || 25; // Default height if not set
        
        verticalPositions.push({
          top: top,
          bottom: top + height + 5 // Add 5px padding
        });
      });
      
      // Find the maximum bottom position
      let maxBottom = 0;
      verticalPositions.forEach(pos => {
        if (pos.bottom > maxBottom) {
          maxBottom = pos.bottom;
        }
      });
      
      // Add padding and set the minimum height
      const newHeight = Math.max(60, maxBottom + 20); // Ensure at least 60px height with padding
      row.style.minHeight = newHeight + 'px';
      
      // Also set the lane title height to match
      const laneTitle = row.querySelector('.roadmap-lane-title');
      if (laneTitle) {
        laneTitle.style.height = (newHeight - 20) + 'px'; // Account for padding
      }
    }
  });
  
  // Second pass to adjust the roadmap-lane-content height
  rows.forEach(row => {
    const content = row.querySelector('.roadmap-lane-content');
    if (content) {
      content.style.height = row.style.minHeight;
    }
  });
}

// Helper function to format date for input[type="date"]
function formatDateForInput(date) {
  const d = new Date(date);
  let month = '' + (d.getMonth() + 1);
  let day = '' + d.getDate();
  const year = d.getFullYear();

  if (month.length < 2) month = '0' + month;
  if (day.length < 2) day = '0' + day;

  return [year, month, day].join('-');
}

// New function to update the roadmap with tasks from the selected material system
function updateRoadmapMaterialTasks(product, materialId) {
  const roadmapContainer = document.getElementById('product-roadmap');
  if (!roadmapContainer) return;
  
  // Hide all material-specific tasks
  roadmapContainer.querySelectorAll('.material-specific').forEach(task => {
    task.style.display = 'none';
  });
  
  // Show tasks for the selected material
  roadmapContainer.querySelectorAll(`.material-task-${materialId}`).forEach(task => {
    task.style.display = 'block';
  });
  
  // Re-adjust row heights after changing visibility
  adjustRowHeights(roadmapContainer);
}

// Fix the renderProductRoadmap function to only show material system tasks in M&P lane
function renderProductRoadmap(product, containerId, startDate = null) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  // Default to today's date if no start date provided
  if (!startDate) {
    startDate = new Date();
  } else if (typeof startDate === 'string') {
    startDate = new Date(startDate);
  }
  
  // Determine the starting quarter based on the date
  const startYear = startDate.getFullYear();
  const startMonth = startDate.getMonth();
  const startQuarter = Math.floor(startMonth / 3) + 1;
  
  // Generate quarters for 5 years (20 quarters)
  const quarters = [];
  let currentYear = startYear;
  let currentQuarter = startQuarter;
  
  for (let i = 0; i < 20; i++) {
    quarters.push(`${currentYear}-Q${currentQuarter}`);
    currentQuarter++;
    if (currentQuarter > 4) {
      currentQuarter = 1;
      currentYear++;
    }
  }
  
  // Get related programs and sort them by need date
  const relatedPrograms = [];
  if (product.programs && product.programs.length > 0) {
    product.programs.forEach(programId => {
      const program = roadmapData.programs.find(p => p.id === programId);
      if (program) {
        relatedPrograms.push(program);
      }
    });
    
    // Sort programs by need date
    relatedPrograms.sort((a, b) => {
      const dateA = a.needDate ? new Date(a.needDate) : new Date('9999-12-31');
      const dateB = b.needDate ? new Date(b.needDate) : new Date('9999-12-31');
      return dateA - dateB;
    });
  }
  
  // Create the roadmap header with quarters and date picker
  let html = `
    <div class="roadmap-container dark-theme">
      <div class="roadmap-timeline-controls">
        <label for="start-date">Start Date:</label>
        <input type="date" id="start-date" class="start-date-picker" value="${formatDateForInput(startDate)}">
      </div>
      <div class="roadmap-timeline">
        <div class="roadmap-header">
          <div class="roadmap-header-lane">Date</div>`;
  
  // Add quarter headers
  quarters.forEach(quarter => {
    const [year, q] = quarter.split('-');
    html += `<div class="roadmap-header-quarter">${year}<br>${q}</div>`;
  });
  
  html += `</div>`;
  
  // Add programs row
  html += `<div class="roadmap-row programs-row">
    <div class="roadmap-lane-title">Programs</div>
    <div class="roadmap-lane-content">`;
  
  // Group programs by quarter to prevent overlapping
  const programsByQuarter = {};
  
  relatedPrograms.forEach(program => {
    if (program.needDate) {
      const needDate = new Date(program.needDate);
      const needYear = needDate.getFullYear();
      const needMonth = needDate.getMonth();
      const needQuarter = Math.floor(needMonth / 3) + 1;
      const needQuarterStr = `${needYear}-Q${needQuarter}`;
      
      if (!programsByQuarter[needQuarterStr]) {
        programsByQuarter[needQuarterStr] = [];
      }
      programsByQuarter[needQuarterStr].push(program);
    }
  });
  
  // Add program markers based on need dates, stacked vertically if needed
  Object.keys(programsByQuarter).forEach(quarter => {
    const quarterIndex = quarters.indexOf(quarter);
    if (quarterIndex >= 0) {
      const position = quarterIndex * 100 + 50;
      const programs = programsByQuarter[quarter];
      
      programs.forEach((program, index) => {
        // Offset each program vertically to prevent overlap
        const verticalOffset = index * 40;
        html += `
          <div class="program-marker" style="left: ${position}px; top: ${verticalOffset}px;" title="${program.name} Need Date: ${formatDate(program.needDate)}">
            <div class="program-marker-point"></div>
            <div class="program-marker-label">${program.name}</div>
          </div>`;
      });
    }
  });
  
  html += `</div></div>`;
  
  // Add milestone row
  html += `<div class="roadmap-row milestone-row">
    <div class="roadmap-lane-title">Milestones</div>
    <div class="roadmap-lane-content">`;
  
  // Group milestones by quarter to prevent overlapping
  const milestonesByQuarter = {};
  
  if (product.milestones && product.milestones.length > 0) {
    product.milestones.forEach(milestone => {
      const date = new Date(milestone.date);
      const year = date.getFullYear();
      const month = date.getMonth();
      const quarter = Math.floor(month / 3) + 1;
      const milestoneQuarter = `${year}-Q${quarter}`;
      
      if (!milestonesByQuarter[milestoneQuarter]) {
        milestonesByQuarter[milestoneQuarter] = [];
      }
      milestonesByQuarter[milestoneQuarter].push(milestone);
    });
  }
  
  // Add milestone markers, stacked vertically if needed
  Object.keys(milestonesByQuarter).forEach(quarter => {
    const quarterIndex = quarters.indexOf(quarter);
    if (quarterIndex >= 0) {
      const position = quarterIndex * 100 + 50;
      const milestones = milestonesByQuarter[quarter];
      
      milestones.forEach((milestone, index) => {
        // Offset each milestone vertically to prevent overlap
        const verticalOffset = index * 40;
        html += `
          <div class="roadmap-milestone" style="left: ${position}px; top: ${verticalOffset}px;" title="${milestone.name}: ${milestone.description}">
            <div class="milestone-marker"></div>
            <div class="milestone-label">${milestone.name}</div>
          </div>`;
      });
    }
  });
  
  html += `</div></div>`;
  
  // Add swimlanes for each category
  const lanes = ["Design", "Manufacturing", "M&P", "Quality"];
  
  lanes.forEach(lane => {
    html += `
      <div class="roadmap-row">
        <div class="roadmap-lane-title">${lane}</div>
        <div class="roadmap-lane-content" data-lane="${lane}">`;
    
    // Group tasks by position to prevent overlapping
    const taskPositions = {};
    
    // For M&P lane, ONLY use material system tasks
    if (lane === "M&P") {
      if (product.materialSystems && product.materialSystems.length > 0) {
        // Get the first material system by default (will be filtered by material filter buttons)
        const firstMaterialId = product.materialSystems[0];
        
        // Process all material systems associated with this product
        product.materialSystems.forEach(materialId => {
          const material = roadmapData.materialSystems.find(ms => ms.id === materialId);
          
          if (material && material.roadmap && material.roadmap.length > 0) {
            material.roadmap.forEach(task => {
              // Calculate position and width based on dates
              const startTaskDate = new Date(task.start);
              const endTaskDate = new Date(task.end);
              
              const startTaskYear = startTaskDate.getFullYear();
              const startTaskMonth = startTaskDate.getMonth();
              const startTaskQuarter = Math.floor(startTaskMonth / 3) + 1;
              const taskStartQuarter = `${startTaskYear}-Q${startTaskQuarter}`;
              
              const endTaskYear = endTaskDate.getFullYear();
              const endTaskMonth = endTaskDate.getMonth();
              const endTaskQuarter = Math.floor(endTaskMonth / 3) + 1;
              const taskEndQuarter = `${endTaskYear}-Q${endTaskQuarter}`;
              
              // Find positions in our quarters array
              const startIndex = quarters.indexOf(taskStartQuarter);
              const endIndex = quarters.indexOf(taskEndQuarter);
              
              // Handle tasks that start before the visible range
              if (endIndex >= 0) { // Only show if the end is visible
                let startPosition = 0;
                let width = 0;
                
                if (startIndex >= 0) {
                  // Task starts within the visible range
                  startPosition = startIndex * 100;
                  width = (endIndex - startIndex + 1) * 100;
                } else {
                  // Task starts before the visible range
                  startPosition = 0; // Start at the beginning of the visible range
                  width = (endIndex + 1) * 100; // Width from beginning to end date
                }
                
                // Create a position key to group overlapping tasks
                const posKey = `${startPosition}-${width}`;
                if (!taskPositions[posKey]) {
                  taskPositions[posKey] = [];
                }
                
                // Set initial display style - only show the first material system's tasks by default
                const initialDisplay = (materialId === firstMaterialId) ? 'block' : 'none';
                
                taskPositions[posKey].push({
                  task: task,
                  source: 'material',
                  materialId: materialId,
                  initialDisplay: initialDisplay
                });
              }
            });
          }
        });
      }
    } 
    // For all other lanes, use product tasks
    else if (product.roadmap && product.roadmap.length > 0) {
      product.roadmap.forEach(task => {
        if (task.lane === lane) {
          // Calculate position and width based on dates
          const startTaskDate = new Date(task.start);
          const endTaskDate = new Date(task.end);
          
          const startTaskYear = startTaskDate.getFullYear();
          const startTaskMonth = startTaskDate.getMonth();
          const startTaskQuarter = Math.floor(startTaskMonth / 3) + 1;
          const taskStartQuarter = `${startTaskYear}-Q${startTaskQuarter}`;
          
          const endTaskYear = endTaskDate.getFullYear();
          const endTaskMonth = endTaskDate.getMonth();
          const endTaskQuarter = Math.floor(endTaskMonth / 3) + 1;
          const taskEndQuarter = `${endTaskYear}-Q${endTaskQuarter}`;
          
          // Find positions in our quarters array
          const startIndex = quarters.indexOf(taskStartQuarter);
          const endIndex = quarters.indexOf(taskEndQuarter);
          
          // Handle tasks that start before the visible range
          if (endIndex >= 0) { // Only show if the end is visible
            let startPosition = 0;
            let width = 0;
            
            if (startIndex >= 0) {
              // Task starts within the visible range
              startPosition = startIndex * 100;
              width = (endIndex - startIndex + 1) * 100;
            } else {
              // Task starts before the visible range
              startPosition = 0; // Start at the beginning of the visible range
              width = (endIndex + 1) * 100; // Width from beginning to end date
            }
            
            // Create a position key to group overlapping tasks
            const posKey = `${startPosition}-${width}`;
            if (!taskPositions[posKey]) {
              taskPositions[posKey] = [];
            }
            taskPositions[posKey].push({
              task: task,
              source: 'product',
              initialDisplay: 'block'
            });
          }
        }
      });
    }
    
    // Render tasks with vertical offsets to prevent overlapping
    Object.keys(taskPositions).forEach(posKey => {
      const [startPosition, width] = posKey.split('-').map(Number);
      const tasks = taskPositions[posKey];
      
      // Sort tasks by start date to ensure consistent ordering
      tasks.sort((a, b) => {
        const dateA = new Date(a.task.start);
        const dateB = new Date(b.task.start);
        return dateA - dateB;
      });
      
      // Calculate optimal vertical spacing based on number of tasks
      const taskHeight = 25; // Base height of a task
      const verticalPadding = 5; // Padding between tasks
      
      tasks.forEach((taskObj, index) => {
        const task = taskObj.task;
        // Determine the class based on status and funding type
        let statusClass = task.status.toLowerCase().replace(/\s+/g, '-');
        if (task.fundingType) {
          statusClass += ` funding-${task.fundingType.toLowerCase().replace(/\s+/g, '-')}`;
        }
        
        // Add material-specific class if it's from a material system
        let materialClass = '';
        if (taskObj.source === 'material') {
          materialClass = ` material-specific material-task-${taskObj.materialId}`;
        }
        
        // Calculate vertical position with better spacing
        const verticalOffset = index * (taskHeight + verticalPadding);
        
        // Create a source indicator for the tooltip
        const sourceText = taskObj.source === 'material' ? 
          `[Material: ${roadmapData.materialSystems.find(ms => ms.id === taskObj.materialId)?.name || taskObj.materialId}] ` : 
          '';
        
        // For the display label, put the task name first, then the source in parentheses
        const displayLabel = taskObj.source === 'material' ? 
          `${task.task} (${roadmapData.materialSystems.find(ms => ms.id === taskObj.materialId)?.name || taskObj.materialId})` : 
          task.task;
        
        // Add display style based on initialDisplay property
        const displayStyle = taskObj.initialDisplay || 'block';
        
        html += `
          <div class="roadmap-task ${statusClass}${materialClass}" 
               style="left: ${startPosition}px; width: ${width}px; top: ${verticalOffset}px; height: ${taskHeight}px; display: ${displayStyle};"
               title="${sourceText}${task.task}: ${formatDate(task.start)} - ${formatDate(task.end)}${task.fundingType ? ' | Funding: ' + task.fundingType : ''}"
               data-source="${taskObj.source}" 
               ${taskObj.materialId ? `data-material-id="${taskObj.materialId}"` : ''}>
            <div class="task-label">${displayLabel}</div>
          </div>`;
      });
    });
    
    html += `</div>
      </div>`;
  });
  
  html += `</div>`;
  
  // Add color key
  html += `
    <div class="roadmap-key">
      <h4>Roadmap Key</h4>
      <div class="key-items">
        <div class="key-item">
          <div class="key-color planned"></div>
          <div class="key-label">Planned</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-sector-irad"></div>
          <div class="key-label">In Development (Sector IRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-division-irad"></div>
          <div class="key-label">In Development (Division IRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-crad"></div>
          <div class="key-label">In Development (CRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color complete"></div>
          <div class="key-label">Complete</div>
        </div>
      </div>
      <p class="roadmap-source-note">Roadmap tasks are sourced from the product's roadmap data and the selected material system.</p>
    </div>`;
  
  container.innerHTML = html;
  
  // Adjust row heights based on content
  adjustRowHeights(container);
  
  // Add event listener for the date picker
  const datePicker = container.querySelector('.start-date-picker');
  if (datePicker) {
    datePicker.addEventListener('change', function() {
      renderProductRoadmap(product, containerId, this.value);
    });
  }
  
  // Add event listeners to tasks for showing task details
  const tasks = container.querySelectorAll('.roadmap-task');
  tasks.forEach(taskElement => {
    taskElement.addEventListener('click', function() {
      const source = this.getAttribute('data-source');
      const materialId = this.getAttribute('data-material-id');
      
      // Find the task data
      const taskLabel = this.querySelector('.task-label').textContent;
      const taskName = taskLabel.includes(']') ? taskLabel.split('] ')[1] : taskLabel;
      
      let taskData;
      if (source === 'material' && materialId) {
        const material = roadmapData.materialSystems.find(ms => ms.id === materialId);
        if (material && material.roadmap) {
          taskData = material.roadmap.find(t => t.task === taskName);
        }
      } else {
        if (product.roadmap) {
          taskData = product.roadmap.find(t => t.task === taskName);
        }
      }
      
      if (taskData) {
        loadTaskDetails(taskData, source, materialId);
      }
    });
  });
}

buildHTML();
fs.watch(dataFilePath, function(eventType, filename) {
  if (filename && eventType === "change") {
    console.log(filename + " has been modified. Regenerating HTML and copying to external repository...");
    buildHTML();
  }
});
