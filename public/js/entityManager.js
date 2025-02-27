// Entity CRUD operations
import { generateId } from './utils.js';
import * as formBuilder from './formBuilder.js';

export function createDefaultEntity(type, existingIds) {
  const defaultEntity = { id: generateId(type, existingIds.map(entity => entity.id)) };
  
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

export function generateFormFields(container, type, entity, roadmapData) {
  container.innerHTML = '';
  
  // Common fields for all entity types
  formBuilder.addFormField(container, 'id', 'ID', entity.id, 'text');
  formBuilder.addFormField(container, 'name', 'Name', entity.name, 'text');
  
  // Type-specific fields
  if (type === 'programs') {
    formBuilder.addFormField(container, 'division', 'Division', entity.division, 'text');
    formBuilder.addFormField(container, 'customerName', 'Customer Name', entity.customerName, 'text');
    formBuilder.addFormField(container, 'missionClass', 'Mission Class', entity.missionClass, 'text');
    formBuilder.addFormField(container, 'needDate', 'Need Date', entity.needDate, 'date');
    formBuilder.addFormField(container, 'closeDate', 'Close Date', entity.closeDate, 'date');
  } 
  else if (type === 'products') {
    // Programs selection (multi-select)
    formBuilder.addMultiSelectField(container, 'programs', entity.programs, roadmapData.programs.map(p => ({ id: p.id, name: p.name })));
    
    // Requirements (nested object)
    formBuilder.addNestedObjectField(container, 'requirements', 'Requirements', entity.requirements || {});
    
    // Material Systems selection (multi-select)
    formBuilder.addMultiSelectField(container, 'materialSystems', entity.materialSystems, roadmapData.materialSystems.map(ms => ({ id: ms.id, name: ms.name })));
    
    // Post Processing (array of strings)
    formBuilder.addArrayField(container, 'postProcessing', 'Post Processing', entity.postProcessing || []);
    
    // Post Processing Suppliers (array of objects)
    formBuilder.addArrayOfObjectsField(container, 'postProcessingSuppliers', 'Post Processing Suppliers', entity.postProcessingSuppliers || [], [
      { name: 'process', label: 'Process', type: 'text' },
      { name: 'supplier', label: 'Supplier', type: 'select', options: roadmapData.suppliers.map(s => ({ id: s.id, name: s.name })) }
    ]);
    
    // Design Tools (array of strings)
    formBuilder.addArrayField(container, 'designTools', 'Design Tools', entity.designTools || []);
    
    // Documentation (array of strings)
    formBuilder.addArrayField(container, 'documentation', 'Documentation', entity.documentation || []);
    
    // Relevant Machines (array of strings)
    formBuilder.addArrayField(container, 'relevantMachines', 'Relevant Machines', entity.relevantMachines || []);
    
    // Relevant Suppliers (multi-select)
    formBuilder.addMultiSelectField(container, 'relevantSuppliers', 'Relevant Suppliers', entity.relevantSuppliers || [], roadmapData.suppliers.map(s => ({ id: s.id, name: s.name })));
    
    // Special NDT (array of strings)
    formBuilder.addArrayField(container, 'specialNDT', 'Special NDT', entity.specialNDT || []);
    
    // Part Acceptance (array of strings)
    formBuilder.addArrayField(container, 'partAcceptance', 'Part Acceptance', entity.partAcceptance || []);
    
    // Product Supply Chain (text)
    formBuilder.addFormField(container, 'productSupplyChain', 'Product Supply Chain', entity.productSupplyChain, 'textarea');
    
    // Roadmap (array of objects)
    const roadmapSection = formBuilder.addAccordionSection(container, 'roadmap', 'Roadmap');
    formBuilder.addArrayOfObjectsField(roadmapSection, 'roadmap', 'Tasks', entity.roadmap || [], [
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
    formBuilder.addArrayOfObjectsField(container, 'milestones', 'Milestones', entity.milestones || [], [
      { name: 'name', label: 'Name', type: 'text' },
      { name: 'date', label: 'Date', type: 'date' },
      { name: 'description', label: 'Description', type: 'text' }
    ]);
  } 
  else if (type === 'materialSystems') {
    formBuilder.addFormField(container, 'process', 'Process', entity.process, 'text');
    formBuilder.addFormField(container, 'material', 'Material', entity.material, 'text');
    formBuilder.addFormField(container, 'qualification', 'Qualification', entity.qualification, 'select', [
      { id: 'Qualified', name: 'Qualified' },
      { id: 'Pending', name: 'Pending' },
      { id: 'In Progress', name: 'In Progress' }
    ]);
    formBuilder.addFormField(container, 'qualificationClass', 'Qualification Class', entity.qualificationClass, 'text');
    formBuilder.addFormField(container, 'supplyChain', 'Supply Chain', entity.supplyChain, 'textarea');
    
    // Properties (nested object)
    formBuilder.addNestedObjectField(container, 'properties', 'Properties', entity.properties || {});
    
    // Processing Parameters (nested object)
    formBuilder.addNestedObjectField(container, 'processingParameters', 'Processing Parameters', entity.processingParameters || {});
    
    // Heat Treatment (nested object)
    formBuilder.addNestedObjectField(container, 'heatTreatment', 'Heat Treatment', entity.heatTreatment || {});
    
    // Post Processing (array of strings)
    formBuilder.addArrayField(container, 'postProcessing', 'Post Processing', entity.postProcessing || []);
    
    // Qualified Machines (array of strings)
    formBuilder.addArrayField(container, 'qualifiedMachines', 'Qualified Machines', entity.qualifiedMachines || []);
    
    // Standard NDT (array of strings)
    formBuilder.addArrayField(container, 'standardNDT', 'Standard NDT', entity.standardNDT || []);
    
    // Roadmap (array of objects)
    formBuilder.addArrayOfObjectsField(container, 'roadmap', 'Roadmap', entity.roadmap || [], [
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
  } 
  else if (type === 'cradOpportunities') {
    formBuilder.addFormField(container, 'relatedEntity', 'Related Entity', entity.relatedEntity, 'text');
    formBuilder.addFormField(container, 'details', 'Details', entity.details, 'textarea');
  } 
  else if (type === 'suppliers') {
    // Materials (multi-select)
    formBuilder.addMultiSelectField(container, 'materials', 'Materials', entity.materials, roadmapData.materialSystems.map(ms => ({ id: ms.id, name: ms.name })));
    
    formBuilder.addFormField(container, 'additionalCapabilities', 'Additional Capabilities', entity.additionalCapabilities, 'textarea');
    
    // Supplier Roadmap (nested object with tasks)
    if (entity.supplierRoadmap) {
      const roadmapSection = formBuilder.addAccordionSection(container, 'supplierRoadmap', 'Supplier Roadmap');
      formBuilder.addArrayOfObjectsField(roadmapSection, 'supplierRoadmap.tasks', 'Tasks', entity.supplierRoadmap.tasks || [], [
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
    formBuilder.addArrayField(container, 'machines', 'Machines', entity.machines?.map(m => m.toString()) || [], 'number');
  }
}

export function updateEntityFromForm(entity, formContainer) {
  // Update basic fields
  const basicFields = formContainer.querySelectorAll('input[type="text"], input[type="date"], input[type="number"], textarea, select');
  basicFields.forEach(field => {
    if (!field.dataset.arrayName && !field.dataset.objectName && !field.dataset.type) {
      entity[field.name] = field.value;
    }
  });
  
  // Update multi-select fields
  const multiSelectFields = formContainer.querySelectorAll('input[type="checkbox"]');
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
    entity[key] = multiSelectValues[key];
  });
  
  // Update nested objects
  const propertyRows = formContainer.querySelectorAll('.properties-container .array-item');
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
    entity[key] = nestedObjects[key];
  });
  
  // Update arrays
  const arrayInputs = formContainer.querySelectorAll('input[data-array-name]');
  const arrayValues = {};
  
  arrayInputs.forEach(input => {
    const arrayName = input.dataset.arrayName;
    if (!arrayValues[arrayName]) {
      arrayValues[arrayName] = [];
    }
    if (input.value) {
      // Convert to number if it's a number input
      const value = input.type === 'number' ? Number(input.value) : input.value;
      arrayValues[arrayName].push(value);
    }
  });
  
  Object.keys(arrayValues).forEach(key => {
    entity[key] = arrayValues[key];
  });
  
  // Update arrays of objects
  const objectFields = formContainer.querySelectorAll('[data-object-name]');
  const objectValues = {};
  
  objectFields.forEach(field => {
    const objectName = field.dataset.objectName;
    const itemIndex = parseInt(field.dataset.itemIndex);
    const fieldName = field.dataset.fieldName;
    
    // Handle nested properties like 'supplierRoadmap.tasks'
    if (objectName.includes('.')) {
      const [parentName, childName] = objectName.split('.');
      
      if (!objectValues[parentName]) {
        objectValues[parentName] = { [childName]: [] };
      }
      
      if (!objectValues[parentName][childName]) {
        objectValues[parentName][childName] = [];
      }
      
      if (!objectValues[parentName][childName][itemIndex]) {
        objectValues[parentName][childName][itemIndex] = {};
      }
      
      objectValues[parentName][childName][itemIndex][fieldName] = field.value;
    } else {
      if (!objectValues[objectName]) {
        objectValues[objectName] = [];
      }
      
      if (!objectValues[objectName][itemIndex]) {
        objectValues[objectName][itemIndex] = {};
      }
      
      objectValues[objectName][itemIndex][fieldName] = field.value;
    }
  });
  
  Object.keys(objectValues).forEach(key => {
    if (key.includes('.')) {
      // Skip, handled below
    } else {
      // Filter out empty objects
      entity[key] = objectValues[key].filter(obj => Object.values(obj).some(val => val));
    }
  });
  
  // Handle nested objects with arrays (like supplierRoadmap.tasks)
  Object.keys(objectValues).forEach(key => {
    if (key.includes('.')) {
      const [parentName, childName] = key.split('.');
      
      if (!entity[parentName]) {
        entity[parentName] = {};
      }
      
      // Filter out empty objects
      entity[parentName][childName] = objectValues[key][childName].filter(obj => Object.values(obj).some(val => val));
    }
  });
  
  return entity;
} 