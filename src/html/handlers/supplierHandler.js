/**
 * Functions for handling supplier details
 * @returns {string} JavaScript code as a string
 */
function getSupplierHandler() {
  console.log('Loading supplier handler module');
  return `
// Supplier details handler
function showSupplierDetails(supplier) {
  console.log('Showing supplier details for:', supplier.name);
  
  // Get materials provided by this supplier
  const relatedMaterials = roadmapData.materialSystems.filter(m => 
    supplier.materials && supplier.materials.includes(m.id)
  );
  
  // Create the detail view HTML
  let html = \`
    <div class="supplier-detail-content">
      <h2>\${supplier.name}</h2>
      
      <div class="supplier-info">
        <p><strong>Location:</strong> \${supplier.location || 'N/A'}</p>
        <p><strong>Contact:</strong> \${supplier.contact || 'N/A'}</p>
        <p><strong>Website:</strong> \${supplier.website ? 
          \`<a href="\${supplier.website}" target="_blank">\${supplier.website}</a>\` : 'N/A'}</p>
        <p><strong>Capabilities:</strong> \${supplier.capabilities || 'N/A'}</p>
      </div>
      
      <h3>Provided Materials</h3>
      <div class="supplier-materials">\`;
  
  // Add related materials
  if (relatedMaterials.length > 0) {
    html += \`<ul class="material-list">\`;
    relatedMaterials.forEach(material => {
      html += \`<li><a href="#" class="material-link" data-material-id="\${material.id}">\${material.name}</a></li>\`;
    });
    html += \`</ul>\`;
  } else {
    html += \`<p>No specific materials listed for this supplier.</p>\`;
  }
  
  html += \`</div>
    
    <h3>Certifications</h3>
    <div class="supplier-certifications">\`;
  
  // Add certifications if they exist
  if (supplier.certifications && supplier.certifications.length > 0) {
    html += \`<ul class="certification-list">\`;
    supplier.certifications.forEach(cert => {
      html += \`<li>\${cert}</li>\`;
    });
    html += \`</ul>\`;
  } else {
    html += \`<p>No certifications listed.</p>\`;
  }
  
  html += \`</div>
    
    <h3>Notes</h3>
    <div class="supplier-notes">
      <p>\${supplier.notes || 'No additional notes available.'}</p>
    </div>
    
    <button class="back-button">Back</button>
    </div>\`;
  
  // Get or create the supplier detail section
  let detailSection = document.getElementById('supplierDetailSection');
  
  // If the section doesn't exist, create it
  if (!detailSection) {
    console.log('Supplier detail section not found, creating it');
    detailSection = document.createElement('div');
    detailSection.id = 'supplierDetailSection';
    detailSection.className = 'detail-view';
    document.querySelector('.container').appendChild(detailSection);
  }
  
  // Set the content
  detailSection.innerHTML = html;
  
  // Add styles for the supplier detail content
  const styleElement = document.createElement('style');
  styleElement.textContent = \`
    .supplier-detail-content {
      padding: 20px;
    }
    .supplier-info {
      background-color: #f5f5f5;
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 20px;
    }
    .material-list, .certification-list {
      list-style-type: none;
      padding: 0;
    }
    .material-list li, .certification-list li {
      margin-bottom: 8px;
    }
    .material-link {
      color: #00269A;
      text-decoration: none;
    }
    .material-link:hover {
      text-decoration: underline;
    }
    .supplier-notes {
      background-color: #fffde7;
      border-left: 4px solid #ffd600;
      padding: 10px 15px;
      margin-bottom: 20px;
    }
  \`;
  document.head.appendChild(styleElement);
  
  // Add event listener to the back button
  detailSection.querySelector('.back-button').addEventListener('click', function(e) {
    e.preventDefault();
    goBack();
  });
  
  // Add event listeners to material links
  detailSection.querySelectorAll('.material-link').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const materialId = this.getAttribute('data-material-id');
      const material = roadmapData.materialSystems.find(m => m.id === materialId);
      if (material) {
        navStack.push('supplierDetailSection');
        showMaterialDetails(material);
      }
    });
  });
  
  // Show the supplier detail section and hide other views
  // First, hide all main views
  document.querySelectorAll('.main-view').forEach(view => {
    view.style.display = 'none';
  });
  
  // Then hide all detail views
  document.querySelectorAll('.detail-view').forEach(view => {
    view.style.display = 'none';
  });
  
  // Finally, show our supplier detail section
  detailSection.style.display = 'block';
  
  // Also update the navigation stack
  navStack.push('supplierDetailSection');
  console.log('Navigation stack updated:', navStack);
}
`;
}

module.exports = { getSupplierHandler }; 