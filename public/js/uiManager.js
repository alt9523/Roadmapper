// UI rendering and event handling
import * as entityManager from './entityManager.js';
import * as formBuilder from './formBuilder.js';

export function renderEntities(container, type, entities, roadmapData, onEntityClick) {
  container.innerHTML = '';
  
  if (!entities || entities.length === 0) {
    container.innerHTML = `<p>No ${type} found. Click "Add" to create one.</p>`;
    return;
  }
  
  entities.forEach((entity, index) => {
    const card = document.createElement('div');
    card.className = 'entity-card';
    card.dataset.index = index;
    
    let cardContent = `<h3>${entity.name || 'Unnamed Entity'}</h3>`;
    
    // Add specific details based on entity type
    if (type === 'programs') {
      cardContent += `
        <p><strong>ID:</strong> ${entity.id || 'N/A'}</p>
        <p><strong>Division:</strong> ${entity.division || 'N/A'}</p>
        <p><strong>Mission Class:</strong> ${entity.missionClass || 'N/A'}</p>
      `;
    } else if (type === 'products') {
      const programNames = entity.programs?.map(progId => {
        const program = roadmapData.programs.find(p => p.id === progId);
        return program ? program.name : progId;
      }).join(', ') || 'None';
      
      cardContent += `
        <p><strong>ID:</strong> ${entity.id || 'N/A'}</p>
        <p><strong>Programs:</strong> ${programNames}</p>
      `;
    } else if (type === 'materialSystems') {
      cardContent += `
        <p><strong>ID:</strong> ${entity.id || 'N/A'}</p>
        <p><strong>Process:</strong> ${entity.process || 'N/A'}</p>
        <p><strong>Material:</strong> ${entity.material || 'N/A'}</p>
        <p><strong>Qualification:</strong> ${entity.qualification || 'N/A'}</p>
      `;
    } else if (type === 'cradOpportunities') {
      cardContent += `
        <p><strong>ID:</strong> ${entity.id || 'N/A'}</p>
        <p><strong>Related Entity:</strong> ${entity.relatedEntity || 'N/A'}</p>
      `;
    } else if (type === 'suppliers') {
      cardContent += `
        <p><strong>ID:</strong> ${entity.id || 'N/A'}</p>
        <p><strong>Materials:</strong> ${entity.materials?.join(', ') || 'None'}</p>
      `;
    }
    
    card.innerHTML = cardContent;
    
    card.addEventListener('click', () => {
      onEntityClick(type, index);
    });
    
    container.appendChild(card);
  });
}

export function setupTabNavigation(tabButtons, tabPanes) {
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabPanes.forEach(pane => pane.classList.remove('active'));
      
      button.classList.add('active');
      document.getElementById(button.dataset.tab).classList.add('active');
    });
  });
}

export function openModal(modal, title) {
  modal.style.display = 'block';
  if (title) {
    const modalTitle = modal.querySelector('.modal-header h2');
    if (modalTitle) {
      modalTitle.textContent = title;
    }
  }
}

export function closeModal(modal) {
  modal.style.display = 'none';
}

export function setupModalClose(modal, closeButton) {
  // Close when clicking the close button
  closeButton.addEventListener('click', () => {
    closeModal(modal);
  });
  
  // Close when clicking outside the modal
  window.addEventListener('click', event => {
    if (event.target === modal) {
      closeModal(modal);
    }
  });
}

// Add other UI functions... 