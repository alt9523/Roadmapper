/**
 * Shows detailed information about a selected material system
 * @param {string} materialId - The ID of the material system to display
 */
function showMaterialDetails(materialId) {
  // Find the material system by ID
  const materialSystem = materialSystems.find(ms => ms.id === materialId);
  
  if (!materialSystem) {
    console.error(`Material system with ID ${materialId} not found`);
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
  modalElement.innerHTML = `
    <div class="modal-content">
      <span class="close-button" onclick="closeModal()">&times;</span>
      <h2>${materialSystem.name}</h2>
      <div class="material-details">
        <p><strong>ID:</strong> ${materialSystem.id}</p>
        <p><strong>Description:</strong> ${materialSystem.description || 'No description available'}</p>
        <p><strong>Properties:</strong></p>
        <ul>
          ${Object.entries(materialSystem.properties || {}).map(([key, value]) => 
            `<li><strong>${key}:</strong> ${value}</li>`).join('')}
        </ul>
      </div>
    </div>
  `;
  
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