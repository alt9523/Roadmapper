/**
 * Functions for handling material system details
 * @returns {string} JavaScript code as a string
 */
function getMaterialHandler() {
  return `
// Material system details handler
function showMaterialDetails(material) {
  console.log('Showing material system details for:', material.name);
  
  // Get related products that use this material
  const relatedProducts = roadmapData.products.filter(p => 
    p.materialSystems && p.materialSystems.includes(material.id)
  );
  
  // Create the detail view HTML
  let html = \`
    <div class="material-detail-content">
      <h2>\${material.name}</h2>
      
      <div class="material-info">
        <p><strong>Material Type:</strong> \${material.type || 'N/A'}</p>
        <p><strong>Qualification Status:</strong> \${material.qualification || 'N/A'}</p>
        <p><strong>Qualification Class:</strong> \${material.qualificationClass || 'N/A'}</p>
        <p><strong>Supplier:</strong> \${material.supplier || 'N/A'}</p>
      </div>
      
      <h3>Properties</h3>
      <div class="material-properties">\`;
  
  // Add material properties if they exist
  if (material.properties) {
    html += \`<table class="properties-table">
      <thead>
        <tr>
          <th>Property</th>
          <th>Value</th>
          <th>Unit</th>
        </tr>
      </thead>
      <tbody>\`;
    
    for (const [key, value] of Object.entries(material.properties)) {
      html += \`
        <tr>
          <td>\${key.charAt(0).toUpperCase() + key.slice(1)}</td>
          <td>\${value.value || 'N/A'}</td>
          <td>\${value.unit || ''}</td>
        </tr>\`;
    }
    
    html += \`</tbody>
    </table>\`;
  } else {
    html += \`<p>No specific properties defined.</p>\`;
  }
  
  html += \`</div>
    
    <h3>Related Products</h3>
    <div class="related-products">\`;
  
  // Add related products
  if (relatedProducts.length > 0) {
    html += \`<ul class="product-list">\`;
    relatedProducts.forEach(product => {
      html += \`<li><a href="#" class="product-link" data-product-id="\${product.id}">\${product.name}</a></li>\`;
    });
    html += \`</ul>\`;
  } else {
    html += \`<p>No products are using this material system.</p>\`;
  }
  
  html += \`</div>
    
    <h3>Material Roadmap</h3>\`;
  
  // Add material roadmap if it exists
  if (material.roadmap && material.roadmap.length > 0) {
    html += \`
      <div class="material-roadmap">
        <table class="roadmap-table">
          <thead>
            <tr>
              <th>Task</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Status</th>
              <th>Funding Type</th>
            </tr>
          </thead>
          <tbody>\`;
    
    material.roadmap.forEach(task => {
      html += \`
        <tr class="\${task.status ? task.status.toLowerCase().replace(/\\s+/g, '-') : ''}">
          <td>\${task.task}</td>
          <td>\${task.start ? new Date(task.start).toLocaleDateString() : 'N/A'}</td>
          <td>\${task.end ? new Date(task.end).toLocaleDateString() : 'N/A'}</td>
          <td>\${task.status || 'N/A'}</td>
          <td>\${task.fundingType || 'N/A'}</td>
        </tr>\`;
    });
    
    html += \`</tbody>
        </table>
      </div>\`;
  } else {
    html += \`<p>No roadmap defined for this material system.</p>\`;
  }
  
  html += \`
    <button class="back-button">Back</button>
    </div>\`;
  
  // Get or create the material detail section
  let detailSection = document.getElementById('materialDetailSection');
  
  // If the section doesn't exist, create it
  if (!detailSection) {
    console.log('Material detail section not found, creating it');
    detailSection = document.createElement('div');
    detailSection.id = 'materialDetailSection';
    detailSection.className = 'detail-view';
    document.querySelector('.container').appendChild(detailSection);
  }
  
  // Set the content
  detailSection.innerHTML = html;
  
  // Add styles for the material detail content
  const styleElement = document.createElement('style');
  styleElement.textContent = \`
    .material-detail-content {
      padding: 20px;
    }
    .material-info {
      background-color: #f5f5f5;
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 20px;
    }
    .properties-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
    }
    .properties-table th, .properties-table td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }
    .properties-table th {
      background-color: #f2f2f2;
    }
    .roadmap-table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
    }
    .roadmap-table th, .roadmap-table td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }
    .roadmap-table th {
      background-color: #f2f2f2;
    }
    .roadmap-table tr.complete {
      background-color: #e8f5e9;
    }
    .roadmap-table tr.in-progress {
      background-color: #e3f2fd;
    }
    .roadmap-table tr.planned {
      background-color: #f5f5f5;
    }
    .product-list {
      list-style-type: none;
      padding: 0;
    }
    .product-list li {
      margin-bottom: 8px;
    }
    .product-link {
      color: #00269A;
      text-decoration: none;
    }
    .product-link:hover {
      text-decoration: underline;
    }
  \`;
  document.head.appendChild(styleElement);
  
  // Add event listener to the back button
  detailSection.querySelector('.back-button').addEventListener('click', function(e) {
    e.preventDefault();
    goBack();
  });
  
  // Add event listeners to product links
  detailSection.querySelectorAll('.product-link').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.getAttribute('data-product-id');
      const product = roadmapData.products.find(p => p.id === productId);
      if (product) {
        navStack.push('materialDetailSection');
        showProductDetails(product);
      }
    });
  });
  
  // Show the material detail section and hide other views
  // First, hide all main views
  document.querySelectorAll('.main-view').forEach(view => {
    view.style.display = 'none';
  });
  
  // Then hide all detail views
  document.querySelectorAll('.detail-view').forEach(view => {
    view.style.display = 'none';
  });
  
  // Finally, show our material detail section
  detailSection.style.display = 'block';
  
  // Also update the navigation stack
  navStack.push('materialDetailSection');
  console.log('Navigation stack updated:', navStack);
}
`;
}

module.exports = { getMaterialHandler }; 