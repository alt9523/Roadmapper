/**
 * Functions for handling product details
 * @returns {string} JavaScript code as a string
 */
function getProductHandler() {
  console.log('Loading product handler module');
  return `
// Product details handler
function showProductDetails(product) {
  console.log('Showing product details for:', product.name);
  const mainContent = document.getElementById('mainContent');
  
  // Check if mainContent exists
  if (!mainContent) {
    console.error('Error: mainContent element not found');
    return;
  }
  
  // Clear previous content
  mainContent.innerHTML = '';
  
  // Create product details container
  const productDetailsContainer = document.createElement('div');
  productDetailsContainer.className = 'product-details-container';
  
  // Create header with back button at top right
  productDetailsContainer.innerHTML = \`
    <div class="product-header">
      <h2>Product Details</h2>
      <button class="back-button" onclick="showProductsView()">Back</button>
    </div>
    
    <div class="product-title-section">
      <h3>\${product.name}</h3>
      
      <div class="product-basic-info">
        \${product.requirements ? \`
          <div class="requirements-section">
            <h4>Requirements</h4>
            \${product.requirements.mechanical ? \`<p><strong>Mechanical:</strong> \${product.requirements.mechanical}</p>\` : ''}
            \${product.requirements.electrical ? \`<p><strong>Electrical:</strong> \${product.requirements.electrical}</p>\` : ''}
            \${product.requirements.environmental ? \`<p><strong>Environmental:</strong> \${product.requirements.environmental}</p>\` : ''}
            \${product.requirements.thermal ? \`<p><strong>Thermal:</strong> \${product.requirements.thermal}</p>\` : ''}
            \${product.requirements.performance ? \`<p><strong>Performance:</strong> \${product.requirements.performance}</p>\` : ''}
          </div>
        \` : ''}
        
        \${product.businessCase ? \`
          <div class="business-case-section">
            <h4>Business Case</h4>
            \${product.businessCase.costSavings ? \`<p><strong>Cost Savings:</strong> \${product.businessCase.costSavings}</p>\` : ''}
            \${product.businessCase.scheduleSavings ? \`<p><strong>Schedule Savings:</strong> \${product.businessCase.scheduleSavings}</p>\` : ''}
            \${product.businessCase.performanceGains ? \`<p><strong>Performance Gains:</strong> \${product.businessCase.performanceGains}</p>\` : ''}
          </div>
        \` : ''}
        
        \${product.productSupplyChain ? \`<p><strong>Make/Buy:</strong> \${product.productSupplyChain}</p>\` : ''}
      </div>
    </div>
  \`;
  
  // Append product details container to main content
  mainContent.appendChild(productDetailsContainer);
  
  // Create quad box container
  const quadBoxContainer = document.createElement('div');
  quadBoxContainer.className = 'quad-box-container';
  mainContent.appendChild(quadBoxContainer);
  
  // Create quad box visualization - ensure the container is in the DOM first
  setTimeout(() => {
    console.log('Creating quad box for:', product.name);
    if (typeof createQuadBox === 'function') {
      createQuadBox(product, quadBoxContainer);
    } else {
      console.error('createQuadBox function not found');
      quadBoxContainer.innerHTML = '<p>Error: Unable to load visualization</p>';
    }
  }, 100); // Increased timeout to ensure DOM is ready
  
  // Create related programs section
  if (product.programs && product.programs.length > 0) {
    const relatedProgramsContainer = document.createElement('div');
    relatedProgramsContainer.className = 'related-programs-container';
    
    // Get program details
    const relatedPrograms = product.programs.map(programId => 
      roadmapData.programs.find(p => p.id === programId)
    ).filter(Boolean);
    
    if (relatedPrograms.length > 0) {
      relatedProgramsContainer.innerHTML = \`
        <h3>Related Programs</h3>
        <div class="program-cards">
          \${relatedPrograms.map(program => \`
            <div class="program-card">
              <h4>\${program.name}</h4>
              <p><span class="status-indicator \${getStatusClass(program)}"></span> \${getStatusText(program)}</p>
            </div>
          \`).join('')}
        </div>
      \`;
      
      mainContent.appendChild(relatedProgramsContainer);
    }
  }
  
  // Add CSS for the product details page
  const style = document.createElement('style');
  style.textContent = \`
    .product-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    
    .back-button {
      background-color: #0056b3;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
    }
    
    .product-title-section {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 30px;
      border-left: 5px solid #6a1b9a;
    }
    
    .product-title-section h3 {
      color: #6a1b9a;
      margin-top: 0;
      margin-bottom: 15px;
      font-size: 24px;
    }
    
    .product-basic-info {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    
    .requirements-section, .business-case-section {
      background-color: white;
      border-radius: 6px;
      padding: 15px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .requirements-section h4, .business-case-section h4 {
      margin-top: 0;
      color: #333;
      border-bottom: 1px solid #ddd;
      padding-bottom: 8px;
      margin-bottom: 12px;
    }
    
    .related-programs-container {
      margin-top: 30px;
    }
    
    .program-cards {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
    }
    
    .program-card {
      background-color: #f8f9fa;
      border-radius: 6px;
      padding: 15px;
      min-width: 200px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .program-card h4 {
      margin-top: 0;
      margin-bottom: 10px;
    }
    
    .status-indicator {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-right: 8px;
    }
    
    .status-planned {
      background-color: #2196F3;
    }
    
    .status-in-progress {
      background-color: #FF9800;
    }
    
    .status-complete {
      background-color: #4CAF50;
    }
    
    .quad-box-container {
      margin-bottom: 30px;
    }
  \`;
  
  document.head.appendChild(style);
}

function getStatusClass(program) {
  // Determine status based on dates or explicit status field
  if (program.status) {
    return \`status-\${program.status.toLowerCase().replace(' ', '-')}\`;
  }
  
  const now = new Date();
  const needDate = program.needDate ? new Date(program.needDate) : null;
  const closeDate = program.closeDate ? new Date(program.closeDate) : null;
  
  if (closeDate && now > closeDate) {
    return 'status-complete';
  } else if (needDate && now > needDate) {
    return 'status-in-progress';
  } else {
    return 'status-planned';
  }
}

function getStatusText(program) {
  if (program.status) {
    return program.status;
  }
  
  const now = new Date();
  const needDate = program.needDate ? new Date(program.needDate) : null;
  const closeDate = program.closeDate ? new Date(program.closeDate) : null;
  
  if (closeDate && now > closeDate) {
    return 'Complete';
  } else if (needDate && now > needDate) {
    return 'In Progress';
  } else {
    return 'Planned';
  }
}
`;
}

module.exports = { getProductHandler }; 