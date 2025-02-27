/**
 * Functions for creating quad box visualizations
 * @returns {string} JavaScript code as a string
 */
function getQuadBoxVisualizer() {
  return `
// Create a quad box visualization for a product
function createQuadBox(product, container) {
  console.log('Creating quad box for product:', product.name);
  
  // Get all material systems for this product
  const materialSystems = product.materialSystems && product.materialSystems.length > 0 
    ? product.materialSystems.map(id => roadmapData.materialSystems.find(m => m.id === id)).filter(Boolean)
    : [];
  
  // Default to first material system if available
  const defaultMaterial = materialSystems.length > 0 ? materialSystems[0] : null;
  
  // Create a specialized quad box layout for product details
  container.innerHTML = \`
    <h3>Product Development Status</h3>
    
    <!-- Material System Filter Buttons -->
    <div class="material-system-filters">
      \${materialSystems.length > 0 ? \`
        <div class="filter-label">Select Material System:</div>
        <div class="filter-buttons">
          \${materialSystems.map((material, index) => \`
            <button class="material-filter-btn \${index === 0 ? 'active' : ''}" 
                    data-material-id="\${material.id}">
              \${material.name}
            </button>
          \`).join('')}
        </div>
      \` : '<p>No material systems available</p>'}
    </div>
    
    <!-- Product Development Progress Module -->
    <div class="product-development-progress">
      <div class="progress-section">
        <h4>TRL</h4>
        <div class="progress-container">
          <div class="progress-bar-wrapper">
            <div class="progress-bar trl-progress" style="width: \${(product.trl || 1) * 11.1}%">
              <span class="progress-current">\${product.trl || 'N/A'}</span>
            </div>
          </div>
          <div class="progress-labels">
            <span class="progress-min">1</span>
            <span class="progress-max">9</span>
          </div>
        </div>
      </div>
      
      <div class="progress-section">
        <h4>MRL</h4>
        <div class="progress-container">
          <div class="progress-bar-wrapper">
            <div class="progress-bar mrl-progress" style="width: \${(defaultMaterial && defaultMaterial.mrl ? defaultMaterial.mrl : 1) * 10}%">
              <span class="progress-current">\${defaultMaterial && defaultMaterial.mrl ? defaultMaterial.mrl : 'N/A'}</span>
            </div>
          </div>
          <div class="progress-labels">
            <span class="progress-min">1</span>
            <span class="progress-max">10</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="specialized-quad-box">
      <!-- Material Systems Quadrant -->
      <div class="quad-section material-section">
        <h4>Material Systems</h4>
        <div class="quad-content material-content">
          \${materialSystems.length > 0 ? materialSystems.map((material, index) => \`
            <div class="material-system-details" id="material-\${material.id}" 
                 style="display: \${index === 0 ? 'block' : 'none'}">
              <h5>\${material.name}</h5>
              <div class="material-details">
                <p><strong>Process:</strong> \${material.process || 'N/A'}</p>
                <p><strong>Qualification:</strong> \${material.qualification || 'N/A'}</p>
                <p><strong>Qualification Class:</strong> \${material.qualificationClass || 'N/A'}</p>
                <p><strong>Statistical Basis:</strong> \${material.statisticalBasis || 'None'}</p>
                
                \${material.postProcessing && material.postProcessing.length > 0 ? \`
                  <div class="material-post-processing">
                    <p><strong>Post Processing:</strong></p>
                    <ul class="post-processing-list" style="list-style-type: disc;">
                      \${material.postProcessing.map(process => \`<li>\${process}</li>\`).join('')}
                    </ul>
                  </div>
                \` : ''}
                
                <div class="view-details-button-container">
                  <button class="view-details-button material-details-btn" 
                          data-material-id="\${material.id}">
                    View Full Details
                  </button>
                </div>
              </div>
            </div>
          \`).join('') : '<p>No material systems specified</p>'}
        </div>
      </div>
      
      <!-- Design Quadrant -->
      <div class="quad-section design-section">
        <h4>Design</h4>
        <div class="quad-content design-content">
          \${product.designTools && product.designTools.length > 0 ? \`
            <h5>Design Tools</h5>
            <ul class="design-list">
              \${product.designTools.map(tool => \`<li>\${tool}</li>\`).join('')}
            </ul>\` : 
            ''
          }
          
          \${product.documentation && product.documentation.length > 0 ? \`
            <h5>Documentation</h5>
            <ul class="design-list">
              \${product.documentation.map(doc => \`<li>\${doc}</li>\`).join('')}
            </ul>\` : 
            ''
          }
        </div>
      </div>
      
      <!-- Manufacturing Quadrant -->
      <div class="quad-section manufacturing-section">
        <h4>Manufacturing</h4>
        <div class="quad-content manufacturing-content">
          \${materialSystems.length > 0 ? materialSystems.map((material, index) => \`
            <div class="manufacturing-for-material" id="manufacturing-\${material.id}" 
                 style="display: \${index === 0 ? 'block' : 'none'}">
              
              <!-- Qualified Machines -->
              \${material.qualifiedMachines && material.qualifiedMachines.length > 0 ? \`
                <div class="qualified-machines">
                  <h5>Qualified Machines</h5>
                  <ul class="machines-list">
                    \${material.qualifiedMachines.map(machine => \`<li>\${machine}</li>\`).join('')}
                  </ul>
                </div>
              \` : ''}
              
              <!-- Relevant Suppliers as Tiles -->
              \${(() => {
                // Find suppliers that support this material
                const relevantSuppliers = roadmapData.suppliers.filter(
                  s => s.materials && s.materials.includes(material.id)
                );
                
                return relevantSuppliers.length > 0 ? \`
                  <div class="relevant-suppliers">
                    <h5>Printing Suppliers</h5>
                    <div class="supplier-tiles">
                      \${relevantSuppliers.map(supplier => \`
                        <div class="supplier-tile">
                          <a href="#" class="supplier-link" data-supplier-id="\${supplier.id}">
                            \${supplier.name}
                          </a>
                        </div>
                      \`).join('')}
                    </div>
                  </div>
                \` : '';
              })()}
              
              <!-- Post Processing Suppliers -->
              \${(() => {
                // Find post processing suppliers for this material
                const postProcessingSuppliers = product.postProcessingSuppliers ? 
                  product.postProcessingSuppliers.filter(pps => {
                    const supplier = roadmapData.suppliers.find(s => s.id === pps.supplier);
                    return supplier;
                  }) : [];
                
                return postProcessingSuppliers.length > 0 ? \`
                  <div class="post-processing-suppliers">
                    <h5>Post Processing Suppliers</h5>
                    <div class="supplier-tiles">
                      \${postProcessingSuppliers.map(ppSupplier => {
                        const supplier = roadmapData.suppliers.find(s => s.id === ppSupplier.supplier);
                        return supplier ? \`
                          <div class="supplier-tile">
                            <a href="#" class="supplier-link" data-supplier-id="\${supplier.id}">
                              <span class="supplier-name">\${supplier.name}</span>
                              <span class="process-name">\${ppSupplier.process}</span>
                            </a>
                          </div>
                        \` : '';
                      }).join('')}
                    </div>
                  </div>
                \` : '';
              })()}
            </div>
          \`).join('') : ''}
          
          <!-- Product-specific manufacturing info (always shown) -->
          \${product.relevantMachines && product.relevantMachines.length > 0 ? \`
            <div class="product-machines">
              <h5>Product-Specific Machines</h5>
              <ul class="machines-list">
                \${product.relevantMachines.map(machine => \`<li>\${machine}</li>\`).join('')}
              </ul>
            </div>\` : 
            ''
          }
        </div>
      </div>
      
      <!-- Quality Quadrant -->
      <div class="quad-section quality-section">
        <h4>Quality</h4>
        <div class="quad-content quality-content">
          \${materialSystems.length > 0 ? materialSystems.map((material, index) => \`
            <div class="quality-for-material" id="quality-\${material.id}" 
                 style="display: \${index === 0 ? 'block' : 'none'}">
              
              <!-- Standard NDT -->
              \${material.standardNDT && material.standardNDT.length > 0 ? \`
                <div class="standard-ndt">
                  <h5>Standard NDT</h5>
                  <ul class="ndt-list">
                    \${material.standardNDT.map(ndt => \`<li>\${ndt}</li>\`).join('')}
                  </ul>
                </div>
              \` : ''}
            </div>
          \`).join('') : ''}
          
          <!-- Product-specific quality info (always shown) -->
          \${product.specialNDT && product.specialNDT.length > 0 ? \`
            <div class="special-ndt">
              <h5>Product Specific NDT</h5>
              <ul class="ndt-list">
                \${product.specialNDT.map(ndt => \`<li>\${ndt}</li>\`).join('')}
              </ul>
            </div>\` : 
            ''
          }
          
          \${product.partAcceptance && product.partAcceptance.length > 0 ? \`
            <div class="part-acceptance">
              <h5>Part Acceptance</h5>
              <ul class="ndt-list">
                \${product.partAcceptance.map(acceptance => \`<li>\${acceptance}</li>\`).join('')}
              </ul>
            </div>\` : 
            ''
          }
        </div>
      </div>
    </div>
    
    <style>
      /* Consistent styling for the quad box */
      .specialized-quad-box {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(2, minmax(250px, auto));
        gap: 15px;
        margin-top: 20px;
      }
      
      .quad-section {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        background-color: #f9f9f9;
        overflow: auto;
        max-height: 350px;
      }
      
      /* Material Systems - Blue */
      .material-section h4 {
        margin-top: 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #0056b3;
        color: #0056b3;
        font-size: 16px;
      }
      
      /* Design - Dark Green */
      .design-section h4 {
        margin-top: 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #2e7d32;
        color: #2e7d32;
        font-size: 16px;
      }
      
      /* Manufacturing - Deep Pink */
      .manufacturing-section h4 {
        margin-top: 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #c2185b;
        color: #c2185b;
        font-size: 16px;
      }
      
      /* Quality - Orange */
      .quality-section h4 {
        margin-top: 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e65100;
        color: #e65100;
        font-size: 16px;
      }
      
      .quad-section h5 {
        color: #333;
        margin: 12px 0 8px 0;
        font-size: 14px;
        font-weight: bold;
      }
      
      .quad-content {
        font-size: 14px;
      }
      
      .quad-content ul {
        margin: 5px 0;
        padding-left: 20px;
      }
      
      .quad-content li {
        margin-bottom: 5px;
      }
      
      /* Supplier tiles styling */
      .supplier-tiles {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 10px;
      }
      
      .supplier-tile {
        background-color: #e6f2ff;
        border-radius: 6px;
        padding: 8px 12px;
        border: 1px solid #c2185b;
        background-color: #fce4ec;
      }
      
      .supplier-tile a {
        text-decoration: none;
        color: #c2185b;
        display: flex;
        flex-direction: column;
      }
      
      .supplier-tile .process-name {
        font-size: 12px;
        color: #666;
        margin-top: 3px;
      }
      
      /* Consistent list styling */
      .machines-list, .ndt-list, .post-processing-list, .design-list {
        list-style-type: disc;
      }
      
      /* Material filter buttons */
      .material-system-filters {
        margin-bottom: 15px;
      }
      
      .filter-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
      }
      
      .material-filter-btn {
        padding: 6px 12px;
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
      }
      
      .material-filter-btn.active {
        background-color: #0056b3;
        color: white;
        border-color: #0056b3;
      }
      
      /* Progress bars */
      .progress-section {
        margin-bottom: 15px;
      }
      
      .progress-bar-wrapper {
        height: 20px;
        background-color: #e9ecef;
        border-radius: 4px;
        margin: 8px 0;
      }
      
      .progress-bar {
        height: 100%;
        border-radius: 4px;
        background-color: #0056b3;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .progress-bar .progress-current {
        color: white;
        font-weight: bold;
        text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
      }
      
      .progress-labels {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
      }
    </style>
    
    <h3>Technical Roadmap</h3>
    <div id="productRoadmapContainer" class="roadmap-container"></div>
  \`;
  
  // Add event listeners to material filter buttons
  container.querySelectorAll('.material-filter-btn').forEach(button => {
    button.addEventListener('click', function() {
      const materialId = this.getAttribute('data-material-id');
      const selectedMaterial = roadmapData.materialSystems.find(m => m.id === materialId);
      
      // Update MRL progress bar based on selected material
      if (selectedMaterial && selectedMaterial.mrl) {
        const mrlProgressBar = container.querySelector('.mrl-progress');
        const mrlCurrentLabel = container.querySelector('.mrl-progress .progress-current');
        
        if (mrlProgressBar) {
          mrlProgressBar.style.width = \`\${selectedMaterial.mrl * 10}%\`;
        }
        
        if (mrlCurrentLabel) {
          mrlCurrentLabel.textContent = \`\${selectedMaterial.mrl}\`;
        }
      }
      
      // Update active button
      container.querySelectorAll('.material-filter-btn').forEach(btn => {
        btn.classList.remove('active');
      });
      this.classList.add('active');
      
      // Hide all material details and show the selected one
      container.querySelectorAll('.material-system-details').forEach(div => {
        div.style.display = 'none';
      });
      container.querySelector(\`#material-\${materialId}\`).style.display = 'block';
      
      // Hide all manufacturing details and show the selected one
      container.querySelectorAll('.manufacturing-for-material').forEach(div => {
        div.style.display = 'none';
      });
      const manufacturingDiv = container.querySelector(\`#manufacturing-\${materialId}\`);
      if (manufacturingDiv) {
        manufacturingDiv.style.display = 'block';
      }
      
      // Hide all quality details and show the selected one
      container.querySelectorAll('.quality-for-material').forEach(div => {
        div.style.display = 'none';
      });
      const qualityDiv = container.querySelector(\`#quality-\${materialId}\`);
      if (qualityDiv) {
        qualityDiv.style.display = 'block';
      }
    });
  });
  
  // Add event listeners to material details buttons
  container.querySelectorAll('.material-details-btn').forEach(button => {
    button.addEventListener('click', function() {
      const materialId = this.getAttribute('data-material-id');
      const material = roadmapData.materialSystems.find(m => m.id === materialId);
      if (material) {
        showMaterialDetails(material);
      }
    });
  });
  
  // Add event listeners to supplier links
  container.querySelectorAll('.supplier-link').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const supplierId = this.getAttribute('data-supplier-id');
      const supplier = roadmapData.suppliers.find(s => s.id === supplierId);
      if (supplier) {
        showSupplierDetails(supplier);
      }
    });
  });
}
`;
}

module.exports = { getQuadBoxVisualizer };