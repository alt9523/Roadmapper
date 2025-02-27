// Add this function to the JavaScript that's being generated or included in the HTML
function generateMaterialSystemScripts() {
  return `
  /**
   * Shows detailed information about a selected material system
   * @param {string} materialId - The ID of the material system to display
   */
  function showMaterialDetails(materialId) {
    // Find the material system by ID
    const materialSystem = materialSystems.find(ms => ms.id === materialId);
    
    if (!materialSystem) {
      console.error(\`Material system with ID \${materialId} not found\`);
      return;
    }
    
    // Get the modal element (create one if it doesn't exist)
    let modalElement = document.getElementById('materialDetailsModal');
    if (!modalElement) {
      modalElement = document.createElement('div');
      modalElement.id = 'materialDetailsModal';
      modalElement.className = 'modal';
      document.body.appendChild(modalElement);
    }
    
    // Populate the modal with material system details
    modalElement.innerHTML = \`
      <div class="modal-content">
        <span class="close-button" onclick="closeModal()">&times;</span>
        <h2>\${materialSystem.name}</h2>
        <div class="material-details">
          <p><strong>ID:</strong> \${materialSystem.id}</p>
          <p><strong>Description:</strong> \${materialSystem.description || 'No description available'}</p>
          <p><strong>Properties:</strong></p>
          <ul>
            \${Object.entries(materialSystem.properties || {}).map(([key, value]) => 
              \`<li><strong>\${key}:</strong> \${value}</li>\`).join('')}
          </ul>
        </div>
      </div>
    \`;
    
    // Display the modal
    modalElement.style.display = 'block';
  }

  /**
   * Closes the material details modal
   */
  function closeModal() {
    const modal = document.getElementById('materialDetailsModal');
    if (modal) {
      modal.style.display = 'none';
    }
  }
  `;
}

// Make sure to include this function's output in your HTML generation
function generateRoadmapHTML() {
  // ... existing code ...
  
  // Add the material system scripts to your HTML
  const scripts = generateMaterialSystemScripts();
  
  // Include the scripts in your HTML output
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <!-- ... existing head content ... -->
      <style>
        /* ... existing styles ... */
        
        /* Modal styles */
        .modal {
          display: none;
          position: fixed;
          z-index: 1000;
          left: 0;
          top: 0;
          width: 100%;
          height: 100%;
          overflow: auto;
          background-color: rgba(0, 0, 0, 0.4);
        }
        
        .modal-content {
          background-color: #fefefe;
          margin: 15% auto;
          padding: 20px;
          border: 1px solid #888;
          width: 80%;
          max-width: 600px;
          border-radius: 5px;
        }
        
        .close-button {
          color: #aaa;
          float: right;
          font-size: 28px;
          font-weight: bold;
          cursor: pointer;
        }
        
        .close-button:hover,
        .close-button:focus {
          color: black;
          text-decoration: none;
          cursor: pointer;
        }
        
        .material-details {
          margin-top: 20px;
        }
      </style>
    </head>
    <body>
      <!-- ... existing body content ... -->
      
      <script>
        // ... existing scripts ...
        
        ${scripts}
      </script>
    </body>
    </html>
  `;
  
  return html;
}

// ... existing code ... 