// Form generation functions
export function addFormField(container, name, label, value, type, options = []) {
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
  
  container.appendChild(formGroup);
}

export function addMultiSelectField(container, name, selectedValues, options) {
  const formGroup = document.createElement('div');
  formGroup.className = 'form-group';
  
  const fieldLabel = document.createElement('label');
  fieldLabel.textContent = name.charAt(0).toUpperCase() + name.slice(1);
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
  container.appendChild(formGroup);
}

export function addNestedObjectField(container, name, label, obj) {
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
  container.appendChild(nestedObject);
}

export function createPropertyRow(objectName, key, value) {
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

export function addArrayField(container, name, label, values, inputType = 'text') {
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
  container.appendChild(formGroup);
}

export function addArrayOfObjectsField(container, name, label, items, fields) {
  const section = document.createElement('div');
  section.className = 'array-of-objects-section';
  
  const sectionHeader = document.createElement('h4');
  sectionHeader.textContent = label;
  section.appendChild(sectionHeader);
  
  const itemsContainer = document.createElement('div');
  itemsContainer.className = 'array-of-objects-container';
  
  // Add existing items
  items.forEach((item, itemIndex) => {
    const itemDiv = createObjectItem(name, label, item, itemIndex, fields);
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
    
    const itemDiv = createObjectItem(name, label, newItem, itemsContainer.children.length, fields);
    itemsContainer.appendChild(itemDiv);
  });
  
  section.appendChild(addButton);
  container.appendChild(section);
}

export function createObjectItem(objectName, label, item, itemIndex, fields) {
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
      select.dataset.objectName = objectName;
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
      input.dataset.objectName = objectName;
      input.dataset.itemIndex = itemIndex;
      input.dataset.fieldName = field.name;
      
      fieldGroup.appendChild(input);
    }
    
    itemDiv.appendChild(fieldGroup);
  });
  
  return itemDiv;
}

export function addAccordionSection(container, name, label) {
  const accordion = document.createElement('div');
  accordion.className = 'accordion';
  accordion.id = `${name}Accordion`;
  
  const header = document.createElement('div');
  header.className = 'accordion-header';
  header.innerHTML = `
    <span>${label}</span>
    <span class="accordion-toggle">▼</span>
  `;
  
  const content = document.createElement('div');
  content.className = 'accordion-content active';
  
  header.addEventListener('click', () => {
    content.classList.toggle('active');
    const toggle = header.querySelector('.accordion-toggle');
    toggle.textContent = content.classList.contains('active') ? '▼' : '▶';
  });
  
  accordion.appendChild(header);
  accordion.appendChild(content);
  container.appendChild(accordion);
  
  return content;
} 