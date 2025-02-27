/**
 * Functions for handling program details
 * @returns {string} JavaScript code as a string
 */
function getProgramHandler() {
  return `
// Program details handler
function showProgramDetails(program) {
  console.log('Showing program details for:', program.id);
  
  // Find products related to this program
  const relatedProducts = roadmapData.products.filter(product => 
    product.programs && product.programs.includes(program.id)
  );
  
  console.log('Related products:', relatedProducts.map(p => p.name));
  
  // Create the program details HTML
  const detailsContent = document.getElementById('programDetailsContent');
  if (!detailsContent) {
    console.error('Program details content element not found');
    return;
  }
  
  // Clear previous content
  detailsContent.innerHTML = '';
  
  // Create the main program information section
  const programInfo = document.createElement('div');
  programInfo.className = 'program-details';
  
  programInfo.innerHTML = \`
    <h1>\${program.name}</h1>
    
    <div class="program-details-info">
      <p><strong>Customer Name:</strong> \${program.customerName || 'N/A'}</p>
      <p><strong>Division:</strong> \${program.division || 'N/A'}</p>
      <p><strong>Mission Class:</strong> \${program.missionClass || 'N/A'}</p>
      <p><strong>Need Date:</strong> \${program.needDate ? formatDate(program.needDate) : 'N/A'}</p>
    </div>
    
    <h2>Products of Interest</h2>
    <div class="products-grid">
      \${relatedProducts.map(product => \`
        <div class="product-card" data-product-id="\${product.id}">
          <h3 class="product-name">\${product.name}</h3>
          <div class="product-status">
            <p><strong>Qual Status:</strong> N/A</p>
            <p><strong>Completion Date:</strong> \${product.completionDate || 'N/A'}</p>
            <p><strong>Implementation Status:</strong> \${product.implementationStatus || 'N/A'}</p>
          </div>
        </div>
      \`).join('')}
    </div>
    
    <button class="back-button">Back</button>
  \`;
  
  // Add the program info to the details content
  detailsContent.appendChild(programInfo);
  
  // Add click handlers to the product cards
  programInfo.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('click', function() {
      const productId = this.getAttribute('data-product-id');
      const product = roadmapData.products.find(p => p.id === productId);
      if (product) {
        showProductDetails(product);
      }
    });
  });
  
  // Add click handler to the back button
  programInfo.querySelector('.back-button').addEventListener('click', function() {
    goBack();
  });
  
  // Show the program details view
  showView('programDetailsView');
}
`;
}

module.exports = { getProgramHandler }; 