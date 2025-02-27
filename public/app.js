// Global state to store the JSON data
let roadmapData = null;
let currentEntity = null;
let currentEntityType = null;
let currentEntityIndex = null;
let isNewEntity = false;

// DOM elements
const saveButton = document.getElementById('saveButton');
const saveStatus = document.getElementById('saveStatus');
const tabButtons = document.querySelectorAll('.tab-button');
const tabPanes = document.querySelectorAll('.tab-pane');
const addButtons = document.querySelectorAll('.add-button');
const entityModal = document.getElementById('entityModal');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
const closeButton = document.querySelector('.close-button');
const saveEntityButton = document.getElementById('saveEntityButton');
const deleteEntityButton = document.getElementById('deleteEntityButton');

// Fetch data from the server
async function fetchData() {
  try {
    showLoadingStatus('Loading data...');
    const response = await fetch('/api/data');
    if (!response.ok) {
      throw new Error('Failed to fetch data');
    }
    roadmapData = await response.json();
    renderAllEntities();
    showSuccessStatus('Data loaded successfully');
  } catch (error) {
    console.error('Error fetching data:', error);
    showErrorStatus('Failed to load data');
  }
}

// Save data to the server
async function saveData() {
  try {
    showLoadingStatus('Saving data...');
    const response = await fetch('/api/data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(roadmapData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to save data');
    }
    
    const result = await response.json();
    showSuccessStatus('Data saved successfully');
    return result;
  } catch (error) {
    console.error('Error saving data:', error);
    showErrorStatus('Failed to save data');
    return { success: false, error: error.message };
  }
}

// Status indicator functions
function showLoadingStatus(message) {
  saveStatus.innerHTML = `<div class="loading"></div> <span>${message}</span>`;
}

function showSuccessStatus(message) {
  saveStatus.innerHTML = `<span class="success-message">${message}</span>`;
  setTimeout(() => {
    saveStatus.innerHTML = '';
  }, 3000);
}

function showErrorStatus(message) {
  saveStatus.innerHTML = `<span class="error-message">${message}</span>`;
}

// Render all entities for each tab
function renderAllEntities() {
  renderEntities('programs', roadmapData.programs);
  renderEntities('products', roadmapData.products);
  renderEntities('materialSystems', roadmapData.materialSystems);
  renderEntities('cradOpportunities', roadmapData.cradOpportunities);
  renderEntities('suppliers', roadmapData.suppliers);
}

// Render entities for a specific tab
function renderEntities(type, entities) {
  const container = document.getElementById(`${type}List`);
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
      openEntityModal(type, index);
    });
    
    container.appendChild(card);
  });
}

// Open the entity modal for editing
function openEntityModal(type, index) {
  currentEntityType = type;
  currentEntityIndex = index;
  isNewEntity = index === -1;
  
  if (isNewEntity) {
    // Create a new entity with default values
    currentEntity = createDefaultEntity(type);
    modalTitle.textContent = `Add New ${type.slice(0, -1).charAt(0).toUpperCase() + type.slice(0, -1).slice(1)}`;
    deleteEntityButton.style.display = 'none';
  } else {
    // Clone the existing entity to avoid direct mutation
    currentEntity = JSON.parse(JSON.stringify(roadmapData[type][index]));
    modalTitle.textContent = `Edit ${currentEntity.name || 'Entity'}`;
    deleteEntityButton.style.display = 'block';
  }
  
  // Generate form fields based on entity type
  generateFormFields(type, currentEntity);
  
  // Show the modal
  entityModal.style.display = 'block';
}

// Create a default entity with required fields
function createDefaultEntity(type) {
  const defaultEntity = { id: generateId(type) };
  
  if (type === 'programs') {
    defaultEntity.name = '';
    defaultEntity.division = '';
    defaultEntity.customerName = 'N/A';
    defaultEntity.missionClass = '';
    defaultEntity.needDate = '';
  } else if (type === 'products') {
    defaultEntity.name = '';
    defaultEntity.requirements = {};
    defaultEntity.programs = [];
    defaultEntity.materialSystems = [];
    defaultEntity.postProcessing = [];
    defaultEntity.roadmap = [];
    defaultEntity.milestones = [];
  } else if (type === 'materialSystems') {
    defaultEntity.name = '';
    defaultEntity.process = '';
    defaultEntity.material = '';
    defaultEntity.qualification = 'Pending';
    defaultEntity.qualificationClass = '';
    defaultEntity.supplyChain = '';
    defaultEntity.properties = {};
    defaultEntity.processingParameters = {};
    defaultEntity.postProcessing = [];
    defaultEntity.qualifiedMachines = [];
    defaultEntity.roadmap = [];
    defaultEntity.standardNDT = [];
  } else if (type === 'cradOpportunities') {
    defaultEntity.name = '';
    defaultEntity.relatedEntity = '';
    defaultEntity.details = '';
  } else if (type === 'suppliers') {
    defaultEntity.name = '';
    defaultEntity.materials = [];
    defaultEntity.additionalCapabilities = '';
  }
  
  return defaultEntity;
}

// Generate a unique ID for a new entity
function generateId(type) {
  const prefix = type === 'programs' ? 'PRG' : 
                 type === 'products' ? 'P' : 
                 type === 'materialSystems' ? 'MS' : 
                 type === 'cradOpportunities' ? 'OPP' : 
                 type === 'suppliers' ? 'SUP' : '';
  
  const existingIds = roadmapData[type].map(entity => entity.id);
  let counter = roadmapData[type].length + 1;
  
  // Find the next available ID
  let newId = `${prefix}${counter}`;
  while (existingIds.includes(newId)) {
    counter++;
    newId = `${prefix}${counter}`;
  }
  
  return newId;
}

// Generate form fields based on entity type and data
function generateFormFields(type, entity) {
  modalBody.innerHTML = '';
  
  // Common fields for all entity types
  addFormField('id', 'ID', entity.id, 'text');
  addFormField('name', 'Name', entity.name, 'text');
  
  // Type-specific fields
  if (type === 'programs') {
    addFormField('division', 'Division', entity.division, 'text');
    addFormField('customerName', 'Customer Name', entity.customerName, 'text');
    addFormField('missionClass', 'Mission Class', entity.missionClass, 'text');
    addFormField('needDate', 'Need Date', entity.needDate, 'date');
    addFormField('closeDate', 'Close Date', entity.closeDate, 'date');
  } 
  else if (type === 'products') {
    // Programs selection (multi-select)
    addMultiSelectField('programs', 'Programs', entity.programs, roadmapData.programs.map(p => ({ id: p.id, name: p.name })));
    
    // Requirements (nested object)
    addNestedObjectField('requirements', 'Requirements', entity.requirements || {});
    
    // Material Systems selection (multi-select)
    addMultiSelectField('materialSystems', 'Material Systems', entity.materialSystems, roadmapData.materialSystems.map(ms => ({ id: ms.id, name: ms.name })));
    
    // Post Processing (array of strings)
    addArrayField('postProcessing', 'Post Processing', entity.postProcessing || []);
    
    // Post Processing Suppliers (array of objects)
    addArrayOfObjectsField('postProcessingSuppliers', 'Post Processing Suppliers', entity.postProcessingSuppliers || [], [
      { name: 'process', label: 'Process', type: 'text' },
      { name: 'supplier', label: 'Supplier', type: 'select', options: roadmapData.suppliers.map(s => ({ id: s.id, name: s.name })) }
    ]);
    
    // Design Tools (array of strings)
    addArrayField('designTools', 'Design Tools', entity.designTools || []);
    
    // Documentation (array of strings)
    addArrayField('documentation', 'Documentation', entity.documentation || []);
    
    // Relevant Machines (array of strings)
    addArrayField('relevantMachines', 'Relevant Machines', entity.relevantMachines || []);
    
    // Relevant Suppliers (multi-select)
    addMultiSelectField('relevantSuppliers', 'Relevant Suppliers', entity.relevantSuppliers || [], roadmapData.suppliers.map(s => ({ id: s.id, name: s.name })));
    
    // Special NDT (array of strings)
    addArrayField('specialNDT', 'Special NDT', entity.specialNDT || []);
    
    // Part Acceptance (array of strings)
    addArrayField('partAcceptance', 'Part Acceptance', entity.partAcceptance || []);
    
    // Product Supply Chain (text)
    addFormField('productSupplyChain', 'Product Supply Chain', entity.productSupplyChain, 'textarea');
    
    // Roadmap (array of objects)
    addAccordionSection('roadmap', 'Roadmap');
    addArrayOfObjectsField('roadmap', 'Tasks', entity.roadmap || [], [
      { name: 'task', label: 'Task Name', type: 'text' },
      { name: 'start', label: 'Start Date', type: 'date' },
      { name: 'end', label: 'End Date', type: 'date' },
      { name: 'status', label: 'Status', type: 'select', options: [
        { id: 'Complete', name: 'Complete' },
        { id: 'In Progress', name: 'In Progress' },
        { id: 'Planned', name: 'Planned' }
      ]},
      { name: 'lane', label: 'Lane', type: 'select', options: [
        { id: 'Design', name: 'Design' },
        { id: 'Manufacturing', name: 'Manufacturing' },
        { id: 'M&P', name: 'M&P' },
        { id: 'Quality', name: 'Quality' }
      ]},
      { name: 'fundingType', label: 'Funding Type', type: 'select', options: [
        { id: 'Division IRAD', name: 'Division IRAD' },
        { id: 'Sector IRAD', name: 'Sector IRAD' },
        { id: 'CRAD', name: 'CRAD' },
        { id: '', name: 'None' }
      ]}
    ]);
    
    // Milestones (array of objects)
    addArrayOfObjectsField('milestones', 'Milestones', entity.milestones || [], [
      { name: 'name', label: 'Name', type: 'text' },
      { name: 'date', label: 'Date', type: 'date' },
      { name: 'description', label: 'Description', type: 'text' }
    ]);
  } 
  else if (type === 'materialSystems') {
    addFormField('process', 'Process', entity.process, 'text');
    addFormField('material', 'Material', entity.material, 'text');
    addFormField('qualification', 'Qualification', entity.qualification, 'select', [
      { id: 'Qualified', name: 'Qualified' },
      { id: 'Pending', name: 'Pending' },
      { id: 'In Progress', name: 'In Progress' }
    ]);
    addFormField('qualificationClass', 'Qualification Class', entity.qualificationClass, 'text');
    addFormField('supplyChain', 'Supply Chain', entity.supplyChain, 'textarea');
    
    // Properties (nested object)
    addNestedObjectField('properties', 'Properties', entity.properties || {});
    
    // Processing Parameters (nested object)
    addNestedObjectField('processingParameters', 'Processing Parameters', entity.processingParameters || {});
    
    // Heat Treatment (nested object)
    addNestedObjectField('heatTreatment', 'Heat Treatment', entity.heatTreatment || {});
    
    // Post Processing (array of strings)
    addArrayField('postProcessing', 'Post Processing', entity.postProcessing || []);
    
    // Qualified Machines (array of strings)
    addArrayField('qualifiedMachines', 'Qualified Machines', entity.qualifiedMachines || []);
    
    // Related Opportunities (multi-select)
    addMultiSelectField('relatedOpportunities', 'Related Opportunities', entity.relatedOpportunities || [], roadmapData.cradOpportunities.map(o => ({ id: o.id, name: o.name })));
    
    // Standard NDT (array of strings)
    addArrayField('standardNDT', 'Standard NDT', entity.standardNDT || []);
    
    // Roadmap (array of objects)
    addArrayOfObjectsField('roadmap', 'Roadmap', entity.roadmap || [], [
      { name: 'task', label: 'Task Name', type: 'text' },
      { name: 'start', label: 'Start Date', type: 'date' },
      { name: 'end', label: 'End Date', type: 'date' },
      { name: 'status', label: 'Status', type: 'select', options: [
        { id: 'Complete', name: 'Complete' },
        { id: 'In Progress', name: 'In Progress' },
        { id: 'Planned', name: 'Planned' }
      ]},
      { name: 'fundingType', label: 'Funding Type', type: 'select', options: [
        { id: 'Division IRAD', name: 'Division IRAD' },
        { id: 'Sector IRAD', name: 'Sector IRAD' },
        { id: 'CRAD', name: 'CRAD' },
        { id: '', name: 'None' }
      ]}
    ]);
    
    // Milestones (array of objects)
    addArrayOfObjectsField('milestones', 'Milestones', entity.milestones || [], [
      { name: 'name', label: 'Name', type: 'text' },
      { name: 'date', label: 'Date', type: 'date' },
      { name: 'description', label: 'Description', type: 'text' }
    ]);
  } 
  else if (type === 'cradOpportunities') {
    addFormField('relatedEntity', 'Related Entity', entity.relatedEntity, 'text');
    addFormField('details', 'Details', entity.details, 'textarea');
  } 
  else if (type === 'suppliers') {
    // Materials (multi-select)
    addMultiSelectField('materials', 'Materials', entity.materials, roadmapData.materialSystems.map(ms => ({ id: ms.id, name: ms.name })));
    
    addFormField('additionalCapabilities', 'Additional Capabilities', entity.additionalCapabilities, 'textarea');
    
    // Supplier Roadmap (array of objects)
    if (entity.supplierRoadmap) {
      addAccordionSection('supplierRoadmap', 'Supplier Roadmap');
      addArrayOfObjectsField('supplierRoadmap.tasks', 'Tasks', entity.supplierRoadmap.tasks || [], [
        { name: 'task', label: 'Task Name', type: 'text' },
        { name: 'start', label: 'Start Date', type: 'date' },
        { name: 'end', label: 'End Date', type: 'date' },
        { name: 'status', label: 'Status', type: 'select', options: [
          { id: 'Complete', name: 'Complete' },
          { id: 'In Progress', name: 'In Progress' },
          { id: 'Planned', name: 'Planned' }
        ]},
        { name: 'category', label: 'Category', type: 'text' },
        { name: 'fundingType', label: 'Funding Type', type: 'select', options: [
          { id: 'Division IRAD', name: 'Division IRAD' },
          { id: 'Sector IRAD', name: 'Sector IRAD' },
          { id: 'CRAD', name: 'CRAD' },
          { id: '', name: 'None' }
        ]}
      ]);
    }
    
    // Machines (array of numbers)
    addArrayField('machines', 'Machines', entity.machines || [], 'number');
  }
}

// Add a basic form field
function addFormField(name, label, value, type, options = []) {
  const formGroup = document.createElement('div');
  formGroup.className = 'form-group';
  
  const fieldLabel = document.createElement('label');
  fieldLabel.setAttribute('for', name);
  fieldLabel.textContent = label;
  formGroup.appendChild(fieldLabel);
  
  if (type === 'textarea') {
    const textarea = document.createElement('textarea');
    textarea.className = 'form-control';
    textarea.id = name;
    textarea.name = name;
    textarea.value = value || '';
    formGroup.appendChild(textarea);
  } 
  else if (type === 'select') {
    const select = document.createElement('select');
    select.className = 'form-control';
    select.id = name;
    select.name = name;
    
    options.forEach(option => {
      const optionElement = document.createElement('option');
      optionElement.value = option.id;
      optionElement.textContent = option.name;
      if (option.id === value) {
        optionElement.selected = true;
      }
      select.appendChild(optionElement);
    });
    
    formGroup.appendChild(select);
  } 
  else {
    const input = document.createElement('input');
    input.className = 'form-control';
    input.type = type;
    input.id = name;
    input.name = name;
    input.value = value || '';
    formGroup.appendChild(input);
  }
  
  modalBody.appendChild(formGroup);
}

// Add a multi-select field
function addMultiSelectField(name, label, selectedValues, options) {
  const formGroup = document.createElement('div');
  formGroup.className = 'form-group';
  
  const fieldLabel = document.createElement('label');
  fieldLabel.textContent = label;
  formGroup.appendChild(fieldLabel);
  
  const checkboxGroup = document.createElement('div');
  checkboxGroup.className = 'checkbox-group';
  
  options.forEach(option => {
    const checkboxItem = document.createElement('div');
    checkboxItem.className = 'checkbox-item';
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `${name}_${option.id}`;
    checkbox.name = name;
    checkbox.value = option.id;
    checkbox.checked = selectedValues?.includes(option.id) || false;
    
    const checkboxLabel = document.createElement('label');
    checkboxLabel.setAttribute('for', `${name}_${option.id}`);
    checkboxLabel.textContent = option.name;
    
    checkboxItem.appendChild(checkbox);
    checkboxItem.appendChild(checkboxLabel);
    checkboxGroup.appendChild(checkboxItem);
  });
  
  formGroup.appendChild(checkboxGroup);
  modalBody.appendChild(formGroup);
}

// Add a nested object field
function addNestedObjectField(name, label, obj) {
  const nestedObject = document.createElement('div');
  nestedObject.className = 'nested-object';
  
  const nestedHeader = document.createElement('h4');
  nestedHeader.textContent = label;
  nestedObject.appendChild(nestedHeader);
  
  // Create a container for dynamic properties
  const propertiesContainer = document.createElement('div');
  propertiesContainer.className = 'properties-container';
  
  // Add existing properties
  Object.entries(obj).forEach(([key, value]) => {
    const propertyRow = createPropertyRow(name, key, value);
    propertiesContainer.appendChild(propertyRow);
  });
  
  nestedObject.appendChild(propertiesContainer);
  
  // Add button to add new property
  const addButton = document.createElement('button');
  addButton.type = 'button';
  addButton.className = 'add-array-item';
  addButton.textContent = 'Add Property';
  addButton.addEventListener('click', () => {
    const propertyRow = createPropertyRow(name, '', '');
    propertiesContainer.appendChild(propertyRow);
  });
  
  nestedObject.appendChild(addButton);
  modalBody.appendChild(nestedObject);
}

// Create a property row for nested objects
function createPropertyRow(objectName, key, value) {
  const propertyRow = document.createElement('div');
  propertyRow.className = 'array-item';
  
  const keyInput = document.createElement('input');
  keyInput.type = 'text';
  keyInput.className = 'form-control';
  keyInput.placeholder = 'Property Name';
  keyInput.value = key;
  keyInput.dataset.type = 'key';
  keyInput.dataset.objectName = objectName;
  
  const valueInput = document.createElement('input');
  valueInput.type = 'text';
  valueInput.className = 'form-control';
  valueInput.placeholder = 'Value';
  valueInput.value = value;
  valueInput.dataset.type = 'value';
  valueInput.dataset.objectName = objectName;
  
  const removeButton = document.createElement('button');
  removeButton.type = 'button';
  removeButton.innerHTML = '&times;';
  removeButton.addEventListener('click', () => {
    propertyRow.remove();
  });
  
  propertyRow.appendChild(keyInput);
  propertyRow.appendChild(valueInput);
  propertyRow.appendChild(removeButton);
  
  return propertyRow;
}

// Add an array field
function addArrayField(name, label, values, inputType = 'text') {
  const formGroup = document.createElement('div');
  formGroup.className = 'form-group';
  
  const fieldLabel = document.createElement('label');
  fieldLabel.textContent = label;
  formGroup.appendChild(fieldLabel);
  
  const arrayItems = document.createElement('div');
  arrayItems.className = 'array-items';
  
  // Add existing items
  values.forEach((value, index) => {
    const arrayItem = document.createElement('div');
    arrayItem.className = 'array-item';
    
    const input = document.createElement('input');
    input.type = inputType;
    input.className = 'form-control';
    input.value = value;
    input.dataset.arrayName = name;
    input.dataset.index = index;
    
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.innerHTML = '&times;';
    removeButton.addEventListener('click', () => {
      arrayItem.remove();
    });
    
    arrayItem.appendChild(input);
    arrayItem.appendChild(removeButton);
    arrayItems.appendChild(arrayItem);
  });
  
  formGroup.appendChild(arrayItems);
  
  // Add button to add new item
  const addButton = document.createElement('button');
  addButton.type = 'button';
  addButton.className = 'add-array-item';
  addButton.textContent = `Add ${label.slice(0, -1) || 'Item'}`;
  addButton.addEventListener('click', () => {
    const arrayItem = document.createElement('div');
    arrayItem.className = 'array-item';
    
    const input = document.createElement('input');
    input.type = inputType;
    input.className = 'form-control';
    input.value = '';
    input.dataset.arrayName = name;
    input.dataset.index = arrayItems.children.length;
    
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.innerHTML = '&times;';
    removeButton.addEventListener('click', () => {
      arrayItem.remove();
    });
    
    arrayItem.appendChild(input);
    arrayItem.appendChild(removeButton);
    arrayItems.appendChild(arrayItem);
  });
  
  formGroup.appendChild(addButton);
  modalBody.appendChild(formGroup);
}

// Add an array of objects field
function addArrayOfObjectsField(name, label, items, fields) {
  const section = document.createElement('div');
  section.className = 'array-of-objects-section';
  
  const sectionHeader = document.createElement('h4');
  sectionHeader.textContent = label;
  section.appendChild(sectionHeader);
  
  const itemsContainer = document.createElement('div');
  itemsContainer.className = 'array-of-objects-container';
  
  // Add existing items
  items.forEach((item, itemIndex) => {
    const itemDiv = document.createElement('div');
    itemDiv.className = 'array-of-objects-item';
    
    // Add a header for each item
    const itemHeader = document.createElement('div');
    itemHeader.className = 'item-header';
    itemHeader.textContent = `${label.slice(0, -1) || 'Item'} ${itemIndex + 1}`;
    
    const removeItemButton = document.createElement('button');
    removeItemButton.type = 'button';
    removeItemButton.className = 'remove-item-button';
    removeItemButton.innerHTML = 'Remove';
    removeItemButton.addEventListener('click', () => {
      itemDiv.remove();
    });
    
    itemHeader.appendChild(removeItemButton);
    itemDiv.appendChild(itemHeader);
    
    // Add fields for this item
    fields.forEach(field => {
      const fieldGroup = document.createElement('div');
      fieldGroup.className = 'field-group';
      
      const fieldLabel = document.createElement('label');
      fieldLabel.textContent = field.label;
      fieldGroup.appendChild(fieldLabel);
      
      if (field.type === 'select') {
        const select = document.createElement('select');
        select.className = 'form-control';
        select.dataset.objectName = name;
        select.dataset.itemIndex = itemIndex;
        select.dataset.fieldName = field.name;
        
        field.options.forEach(option => {
          const optionElement = document.createElement('option');
          optionElement.value = option.id;
          optionElement.textContent = option.name;
          if (item[field.name] === option.id) {
            optionElement.selected = true;
          }
          select.appendChild(optionElement);
        });
        
        fieldGroup.appendChild(select);
      } else {
        const input = document.createElement('input');
        input.type = field.type;
        input.className = 'form-control';
        input.value = item[field.name] || '';
        input.dataset.objectName = name;
        input.dataset.itemIndex = itemIndex;
        input.dataset.fieldName = field.name;
        
        fieldGroup.appendChild(input);
      }
      
      itemDiv.appendChild(fieldGroup);
    });
    
    itemsContainer.appendChild(itemDiv);
  });
  
  section.appendChild(itemsContainer);
  
  // Add button to add new item
  const addButton = document.createElement('button');
  addButton.type = 'button';
  addButton.className = 'add-array-item';
  addButton.textContent = `Add ${label.slice(0, -1) || 'Item'}`;
  addButton.addEventListener('click', () => {
    const newItem = {};
    fields.forEach(field => {
      newItem[field.name] = '';
    });
    
    const itemDiv = document.createElement('div');
    itemDiv.className = 'array-of-objects-item';
    
    // Add a header for the new item
    const itemHeader = document.createElement('div');
    itemHeader.className = 'item-header';
    itemHeader.textContent = `${label.slice(0, -1) || 'Item'} ${itemsContainer.children.length + 1}`;
    
    const removeItemButton = document.createElement('button');
    removeItemButton.type = 'button';
    removeItemButton.className = 'remove-item-button';
    removeItemButton.innerHTML = 'Remove';
    removeItemButton.addEventListener('click', () => {
      itemDiv.remove();
    });
    
    itemHeader.appendChild(removeItemButton);
    itemDiv.appendChild(itemHeader);
    
    // Add fields for this item
    fields.forEach(field => {
      const fieldGroup = document.createElement('div');
      fieldGroup.className = 'field-group';
      
      const fieldLabel = document.createElement('label');
      fieldLabel.textContent = field.label;
      fieldGroup.appendChild(fieldLabel);
      
      if (field.type === 'select') {
        const select = document.createElement('select');
        select.className = 'form-control';
        select.dataset.objectName = name;
        select.dataset.itemIndex = itemsContainer.children.length;
        select.dataset.fieldName = field.name;
        
        field.options.forEach(option => {
          const optionElement = document.createElement('option');
          optionElement.value = option.id;
          optionElement.textContent = option.name;
          select.appendChild(optionElement);
        });
        
        fieldGroup.appendChild(select);
      } else {
        const input = document.createElement('input');
        input.type = field.type;
        input.className = 'form-control';
        input.value = '';
        input.dataset.objectName = name;
        input.dataset.itemIndex = itemsContainer.children.length;
        input.dataset.fieldName = field.name;
        
        fieldGroup.appendChild(input);
      }
      
      itemDiv.appendChild(fieldGroup);
    });
    
    itemsContainer.appendChild(itemDiv);
  });
  
  section.appendChild(addButton);
  modalBody.appendChild(section);
}

// Add an accordion section
function addAccordionSection(name, label) {
  const accordion = document.createElement('div');
  accordion.className = 'accordion';
  
  const accordionHeader = document.createElement('div');
  accordionHeader.className = 'accordion-header';
  accordionHeader.textContent = label;
  
  const accordionContent = document.createElement('div');
  accordionContent.className = 'accordion-content';
  accordionContent.id = `${name}-content`;
  
  accordionHeader.addEventListener('click', () => {
    accordionContent.classList.toggle('active');
  });
  
  accordion.appendChild(accordionHeader);
  accordion.appendChild(accordionContent);
  
  modalBody.appendChild(accordion);
}

// Save the current entity
function saveCurrentEntity() {
  // Update the entity with form values
  updateEntityFromForm();
  
  if (isNewEntity) {
    // Add the new entity to the data
    roadmapData[currentEntityType].push(currentEntity);
  } else {
    // Update the existing entity
    roadmapData[currentEntityType][currentEntityIndex] = currentEntity;
  }
  
  // Close the modal
  closeModal();
  
  // Re-render the entities
  renderEntities(currentEntityType, roadmapData[currentEntityType]);
}

// Delete the current entity
function deleteCurrentEntity() {
  if (confirm(`Are you sure you want to delete this ${currentEntityType.slice(0, -1)}?`)) {
    // Remove the entity from the data
    roadmapData[currentEntityType].splice(currentEntityIndex, 1);
    
    // Close the modal
    closeModal();
    
    // Re-render the entities
    renderEntities(currentEntityType, roadmapData[currentEntityType]);
  }
}

// Update the entity with form values
function updateEntityFromForm() {
  // Update basic fields
  const basicFields = modalBody.querySelectorAll('input[type="text"], input[type="date"], input[type="number"], textarea, select');
  basicFields.forEach(field => {
    if (!field.dataset.arrayName && !field.dataset.objectName && !field.dataset.type) {
      currentEntity[field.name] = field.value;
    }
  });
  
  // Update multi-select fields
  const multiSelectFields = modalBody.querySelectorAll('input[type="checkbox"]');
  const multiSelectValues = {};
  
  multiSelectFields.forEach(field => {
    const name = field.name;
    if (!multiSelectValues[name]) {
      multiSelectValues[name] = [];
    }
    if (field.checked) {
      multiSelectValues[name].push(field.value);
    }
  });
  
  Object.keys(multiSelectValues).forEach(key => {
    currentEntity[key] = multiSelectValues[key];
  });
  
  // Update nested objects
  const propertyRows = modalBody.querySelectorAll('.properties-container .array-item');
  const nestedObjects = {};
  
  propertyRows.forEach(row => {
    const keyInput = row.querySelector('input[data-type="key"]');
    const valueInput = row.querySelector('input[data-type="value"]');
    const objectName = keyInput.dataset.objectName;
    
    if (!nestedObjects[objectName]) {
      nestedObjects[objectName] = {};
    }
    
    if (keyInput.value) {
      nestedObjects[objectName][keyInput.value] = valueInput.value;
    }
  });
  
  Object.keys(nestedObjects).forEach(key => {
    currentEntity[key] = nestedObjects[key];
  });
  
  // Update arrays
  const arrayInputs = modalBody.querySelectorAll('input[data-array-name]');
  const arrayValues = {};
  
  arrayInputs.forEach(input => {
    const arrayName = input.dataset.arrayName;
    if (!arrayValues[arrayName]) {
      arrayValues[arrayName] = [];
    }
    if (input.value) {
      arrayValues[arrayName].push(input.value);
    }
  });
  
  Object.keys(arrayValues).forEach(key => {
    currentEntity[key] = arrayValues[key];
  });
  
  // Update arrays of objects
  const objectFields = modalBody.querySelectorAll('[data-object-name]');
  const objectValues = {};
  
  objectFields.forEach(field => {
    const objectName = field.dataset.objectName;
    const itemIndex = parseInt(field.dataset.itemIndex);
    const fieldName = field.dataset.fieldName;
    
    if (!objectValues[objectName]) {
      objectValues[objectName] = [];
    }
    
    if (!objectValues[objectName][itemIndex]) {
      objectValues[objectName][itemIndex] = {};
    }
    
    objectValues[objectName][itemIndex][fieldName] = field.value;
  });
  
  Object.keys(objectValues).forEach(key => {
    // Filter out empty objects
    currentEntity[key] = objectValues[key].filter(obj => Object.values(obj).some(val => val));
  });
}

// Close the modal
function closeModal() {
  entityModal.style.display = 'none';
  currentEntity = null;
  currentEntityType = null;
  currentEntityIndex = null;
  isNewEntity = false;
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Fetch data when the page loads
  fetchData();
  
  // Tab navigation
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabPanes.forEach(pane => pane.classList.remove('active'));
      
      button.classList.add('active');
      document.getElementById(button.dataset.tab).classList.add('active');
    });
  });
  
  // Add entity buttons
  addButtons.forEach(button => {
    button.addEventListener('click', () => {
      openEntityModal(button.dataset.type, -1);
    });
  });
  
  // Save button
  saveButton.addEventListener('click', saveData);
  
  // Close modal button
  closeButton.addEventListener('click', closeModal);
  
  // Save entity button
  saveEntityButton.addEventListener('click', saveCurrentEntity);
  
  // Delete entity button
  deleteEntityButton.addEventListener('click', deleteCurrentEntity);
  
  // Close modal when clicking outside
  window.addEventListener('click', event => {
    if (event.target === entityModal) {
      closeModal();
    }
  });
}); 