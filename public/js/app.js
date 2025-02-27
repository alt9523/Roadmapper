// Main application entry point
import dataService from './dataService.js';
import * as uiManager from './uiManager.js';
import * as entityManager from './entityManager.js';
import { showLoadingStatus, showSuccessStatus, showErrorStatus } from './utils.js';

// Global state
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

// Initialize the application
async function init() {
  try {
    // Set up event listeners
    setupEventListeners();
    
    // Fetch initial data
    await fetchData();
  } catch (error) {
    console.error('Failed to initialize application:', error);
  }
}

// Fetch data from the server
async function fetchData() {
  try {
    showLoadingStatus(saveStatus, 'Loading data...');
    roadmapData = await dataService.fetchData();
    renderAllEntities();
    showSuccessStatus(saveStatus, 'Data loaded successfully');
  } catch (error) {
    showErrorStatus(saveStatus, 'Failed to load data');
  }
}

// Save data to the server
async function saveData() {
  try {
    showLoadingStatus(saveStatus, 'Saving data...');
    await dataService.saveData(roadmapData);
    showSuccessStatus(saveStatus, 'Data saved successfully');
  } catch (error) {
    showErrorStatus(saveStatus, 'Failed to save data');
  }
}

// Render all entities
function renderAllEntities() {
  const types = ['programs', 'products', 'materialSystems', 'cradOpportunities', 'suppliers'];
  types.forEach(type => {
    const container = document.getElementById(`${type}List`);
    uiManager.renderEntities(container, type, roadmapData[type], roadmapData, openEntityModal);
  });
}

// Open entity modal
function openEntityModal(type, index) {
  isNewEntity = index === -1;
  currentEntityType = type;
  currentEntityIndex = index;
  
  if (isNewEntity) {
    // Create a new entity
    currentEntity = entityManager.createDefaultEntity(type, roadmapData[type]);
    modalTitle.textContent = `Add New ${type.slice(0, -1).charAt(0).toUpperCase() + type.slice(0, -1).slice(1)}`;
    deleteEntityButton.style.display = 'none';
  } else {
    // Edit existing entity
    currentEntity = { ...roadmapData[type][index] };
    modalTitle.textContent = `Edit ${currentEntity.name || 'Entity'}`;
    deleteEntityButton.style.display = 'block';
  }
  
  // Generate form fields
  entityManager.generateFormFields(modalBody, type, currentEntity, roadmapData);
  
  // Show the modal
  uiManager.openModal(entityModal);
}

// Save the current entity
function saveCurrentEntity() {
  // Update entity from form
  entityManager.updateEntityFromForm(currentEntity, modalBody);
  
  if (isNewEntity) {
    // Add new entity
    roadmapData[currentEntityType].push(currentEntity);
  } else {
    // Update existing entity
    roadmapData[currentEntityType][currentEntityIndex] = currentEntity;
  }
  
  // Close the modal
  uiManager.closeModal(entityModal);
  
  // Re-render entities
  renderAllEntities();
  
  // Show success message
  showSuccessStatus(saveStatus, `${currentEntity.name || 'Entity'} saved successfully. Don't forget to click "Save Changes" to persist your changes.`);
  
  // Reset current entity
  currentEntity = null;
  currentEntityType = null;
  currentEntityIndex = null;
  isNewEntity = false;
}

// Delete the current entity
function deleteCurrentEntity() {
  if (confirm(`Are you sure you want to delete ${currentEntity.name || 'this entity'}?`)) {
    // Remove entity from the array
    roadmapData[currentEntityType].splice(currentEntityIndex, 1);
    
    // Close the modal
    uiManager.closeModal(entityModal);
    
    // Re-render entities
    renderAllEntities();
    
    // Show success message
    showSuccessStatus(saveStatus, `Entity deleted successfully. Don't forget to click "Save Changes" to persist your changes.`);
    
    // Reset current entity
    currentEntity = null;
    currentEntityType = null;
    currentEntityIndex = null;
    isNewEntity = false;
  }
}

// Close the modal
function closeModal() {
  uiManager.closeModal(entityModal);
  currentEntity = null;
  currentEntityType = null;
  currentEntityIndex = null;
  isNewEntity = false;
}

// Set up event listeners
function setupEventListeners() {
  // Tab navigation
  uiManager.setupTabNavigation(tabButtons, tabPanes);
  
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
  
  // Modal close setup
  uiManager.setupModalClose(entityModal, closeButton);
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init); 