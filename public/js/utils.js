// Utility functions
export function generateId(type, existingIds) {
  const prefix = type === 'programs' ? 'PRG' : 
                 type === 'products' ? 'P' : 
                 type === 'materialSystems' ? 'MS' : 
                 type === 'cradOpportunities' ? 'OPP' : 
                 type === 'suppliers' ? 'SUP' : '';
  
  let counter = existingIds.length + 1;
  
  // Find the next available ID
  let newId = `${prefix}${counter}`;
  while (existingIds.includes(newId)) {
    counter++;
    newId = `${prefix}${counter}`;
  }
  
  return newId;
}

export function showLoadingStatus(element, message) {
  element.innerHTML = `<div class="loading"></div> <span>${message}</span>`;
}

export function showSuccessStatus(element, message) {
  element.innerHTML = `<span class="success-message">${message}</span>`;
  setTimeout(() => {
    element.innerHTML = '';
  }, 3000);
}

export function showErrorStatus(element, message) {
  element.innerHTML = `<span class="error-message">${message}</span>`;
} 