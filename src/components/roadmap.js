// Roadmap rendering logic
const { formatDate, formatDateForInput, getStatusColor } = require('../utils/dateUtils');
const { adjustRowHeights } = require('../utils/domUtils');
const { navStack } = require('../utils/navigation');

/**
 * Updates the roadmap to show tasks from the selected material system
 * @param {Object} product - The product object
 * @param {string} materialId - The material system ID to show
 */
function updateRoadmapMaterialTasks(product, materialId) {
  const roadmapContainer = document.getElementById('product-roadmap');
  if (!roadmapContainer) return;
  
  // Hide all material-specific tasks
  roadmapContainer.querySelectorAll('.material-specific').forEach(task => {
    task.style.display = 'none';
  });
  
  // Show tasks for the selected material
  roadmapContainer.querySelectorAll(`.material-task-${materialId}`).forEach(task => {
    task.style.display = 'block';
  });
  
  // Re-adjust row heights after changing visibility
  adjustRowHeights(roadmapContainer);
}

/**
 * Renders a product roadmap
 * @param {Object} product - The product object
 * @param {string} containerId - The ID of the container element
 * @param {Date|string|null} startDate - The start date for the roadmap
 * @param {Object} roadmapData - The complete roadmap data
 */
function renderProductRoadmap(product, containerId, startDate = null, roadmapData) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  // Default to today's date if no start date provided
  if (!startDate) {
    startDate = new Date();
  } else if (typeof startDate === 'string') {
    startDate = new Date(startDate);
  }
  
  // Determine the starting quarter based on the date
  const startYear = startDate.getFullYear();
  const startMonth = startDate.getMonth();
  const startQuarter = Math.floor(startMonth / 3) + 1;
  
  // Generate quarters for 5 years (20 quarters)
  const quarters = [];
  let currentYear = startYear;
  let currentQuarter = startQuarter;
  
  for (let i = 0; i < 20; i++) {
    quarters.push(`${currentYear}-Q${currentQuarter}`);
    currentQuarter++;
    if (currentQuarter > 4) {
      currentQuarter = 1;
      currentYear++;
    }
  }
  
  // Get related programs and sort them by need date
  const relatedPrograms = [];
  if (product.programs && product.programs.length > 0) {
    product.programs.forEach(programId => {
      const program = roadmapData.programs.find(p => p.id === programId);
      if (program) {
        relatedPrograms.push(program);
      }
    });
    
    // Sort programs by need date
    relatedPrograms.sort((a, b) => {
      const dateA = a.needDate ? new Date(a.needDate) : new Date('9999-12-31');
      const dateB = b.needDate ? new Date(b.needDate) : new Date('9999-12-31');
      return dateA - dateB;
    });
  }
  
  // Create the roadmap header with quarters and date picker
  let html = `
    <div class="roadmap-container dark-theme">
      <div class="roadmap-timeline-controls">
        <label for="start-date">Start Date:</label>
        <input type="date" id="start-date" class="start-date-picker" value="${formatDateForInput(startDate)}">
      </div>
      <div class="roadmap-timeline">
        <div class="roadmap-header">
          <div class="roadmap-header-lane">Date</div>`;
  
  // Add quarter headers
  quarters.forEach(quarter => {
    const [year, q] = quarter.split('-');
    html += `<div class="roadmap-header-quarter">${year}<br>${q}</div>`;
  });
  
  html += `</div>`;
  
  // Add programs row
  html += `<div class="roadmap-row programs-row">
    <div class="roadmap-lane-title">Programs</div>
    <div class="roadmap-lane-content">`;
  
  // Group programs by quarter to prevent overlapping
  const programsByQuarter = {};
  
  relatedPrograms.forEach(program => {
    if (program.needDate) {
      const needDate = new Date(program.needDate);
      const needYear = needDate.getFullYear();
      const needMonth = needDate.getMonth();
      const needQuarter = Math.floor(needMonth / 3) + 1;
      const needQuarterStr = `${needYear}-Q${needQuarter}`;
      
      if (!programsByQuarter[needQuarterStr]) {
        programsByQuarter[needQuarterStr] = [];
      }
      programsByQuarter[needQuarterStr].push(program);
    }
  });
  
  // Add program markers based on need dates, stacked vertically if needed
  Object.keys(programsByQuarter).forEach(quarter => {
    const quarterIndex = quarters.indexOf(quarter);
    if (quarterIndex >= 0) {
      const position = quarterIndex * 100 + 50;
      const programs = programsByQuarter[quarter];
      
      programs.forEach((program, index) => {
        // Offset each program vertically to prevent overlap
        const verticalOffset = index * 40;
        html += `
          <div class="program-marker" style="left: ${position}px; top: ${verticalOffset}px;" title="${program.name} Need Date: ${formatDate(program.needDate)}">
            <div class="program-marker-point"></div>
            <div class="program-marker-label">${program.name}</div>
          </div>`;
      });
    }
  });
  
  html += `</div></div>`;
  
  // Add milestone row
  html += `<div class="roadmap-row milestone-row">
    <div class="roadmap-lane-title">Milestones</div>
    <div class="roadmap-lane-content">`;
  
  // Group milestones by quarter to prevent overlapping
  const milestonesByQuarter = {};
  
  if (product.milestones && product.milestones.length > 0) {
    product.milestones.forEach(milestone => {
      const date = new Date(milestone.date);
      const year = date.getFullYear();
      const month = date.getMonth();
      const quarter = Math.floor(month / 3) + 1;
      const milestoneQuarter = `${year}-Q${quarter}`;
      
      if (!milestonesByQuarter[milestoneQuarter]) {
        milestonesByQuarter[milestoneQuarter] = [];
      }
      milestonesByQuarter[milestoneQuarter].push(milestone);
    });
  }
  
  // Add milestone markers, stacked vertically if needed
  Object.keys(milestonesByQuarter).forEach(quarter => {
    const quarterIndex = quarters.indexOf(quarter);
    if (quarterIndex >= 0) {
      const position = quarterIndex * 100 + 50;
      const milestones = milestonesByQuarter[quarter];
      
      milestones.forEach((milestone, index) => {
        // Offset each milestone vertically to prevent overlap
        const verticalOffset = index * 40;
        html += `
          <div class="roadmap-milestone" style="left: ${position}px; top: ${verticalOffset}px;" title="${milestone.name}: ${milestone.description}">
            <div class="milestone-marker"></div>
            <div class="milestone-label">${milestone.name}</div>
          </div>`;
      });
    }
  });
  
  html += `</div></div>`;
  
  // Add swimlanes for each category
  const lanes = ["Design", "Manufacturing", "M&P", "Quality"];
  
  lanes.forEach(lane => {
    html += `
      <div class="roadmap-row">
        <div class="roadmap-lane-title">${lane}</div>
        <div class="roadmap-lane-content" data-lane="${lane}">`;
    
    // Group tasks by position to prevent overlapping
    const taskPositions = {};
    
    // For M&P lane, ONLY use material system tasks
    if (lane === "M&P") {
      if (product.materialSystems && product.materialSystems.length > 0) {
        // Get the first material system by default (will be filtered by material filter buttons)
        const firstMaterialId = product.materialSystems[0];
        
        // Process all material systems associated with this product
        product.materialSystems.forEach(materialId => {
          const material = roadmapData.materialSystems.find(ms => ms.id === materialId);
          
          if (material && material.roadmap && material.roadmap.length > 0) {
            material.roadmap.forEach(task => {
              // Calculate position and width based on dates
              const startTaskDate = new Date(task.start);
              const endTaskDate = new Date(task.end);
              
              const startTaskYear = startTaskDate.getFullYear();
              const startTaskMonth = startTaskDate.getMonth();
              const startTaskQuarter = Math.floor(startTaskMonth / 3) + 1;
              const taskStartQuarter = `${startTaskYear}-Q${startTaskQuarter}`;
              
              const endTaskYear = endTaskDate.getFullYear();
              const endTaskMonth = endTaskDate.getMonth();
              const endTaskQuarter = Math.floor(endTaskMonth / 3) + 1;
              const taskEndQuarter = `${endTaskYear}-Q${endTaskQuarter}`;
              
              // Find positions in our quarters array
              const startIndex = quarters.indexOf(taskStartQuarter);
              const endIndex = quarters.indexOf(taskEndQuarter);
              
              // Handle tasks that start before the visible range
              if (endIndex >= 0) { // Only show if the end is visible
                let startPosition = 0;
                let width = 0;
                
                if (startIndex >= 0) {
                  // Task starts within the visible range
                  startPosition = startIndex * 100;
                  width = (endIndex - startIndex + 1) * 100;
                } else {
                  // Task starts before the visible range
                  startPosition = 0; // Start at the beginning of the visible range
                  width = (endIndex + 1) * 100; // Width from beginning to end date
                }
                
                // Create a position key to group overlapping tasks
                const posKey = `${startPosition}-${width}`;
                if (!taskPositions[posKey]) {
                  taskPositions[posKey] = [];
                }
                
                // Set initial display style - only show the first material system's tasks by default
                const initialDisplay = (materialId === firstMaterialId) ? 'block' : 'none';
                
                taskPositions[posKey].push({
                  task: task,
                  source: 'material',
                  materialId: materialId,
                  initialDisplay: initialDisplay
                });
              }
            });
          }
        });
      }
    } 
    // For all other lanes, use product tasks
    else if (product.roadmap && product.roadmap.length > 0) {
      product.roadmap.forEach(task => {
        if (task.lane === lane) {
          // Calculate position and width based on dates
          const startTaskDate = new Date(task.start);
          const endTaskDate = new Date(task.end);
          
          const startTaskYear = startTaskDate.getFullYear();
          const startTaskMonth = startTaskDate.getMonth();
          const startTaskQuarter = Math.floor(startTaskMonth / 3) + 1;
          const taskStartQuarter = `${startTaskYear}-Q${startTaskQuarter}`;
          
          const endTaskYear = endTaskDate.getFullYear();
          const endTaskMonth = endTaskDate.getMonth();
          const endTaskQuarter = Math.floor(endTaskMonth / 3) + 1;
          const taskEndQuarter = `${endTaskYear}-Q${endTaskQuarter}`;
          
          // Find positions in our quarters array
          const startIndex = quarters.indexOf(taskStartQuarter);
          const endIndex = quarters.indexOf(taskEndQuarter);
          
          // Handle tasks that start before the visible range
          if (endIndex >= 0) { // Only show if the end is visible
            let startPosition = 0;
            let width = 0;
            
            if (startIndex >= 0) {
              // Task starts within the visible range
              startPosition = startIndex * 100;
              width = (endIndex - startIndex + 1) * 100;
            } else {
              // Task starts before the visible range
              startPosition = 0; // Start at the beginning of the visible range
              width = (endIndex + 1) * 100; // Width from beginning to end date
            }
            
            // Create a position key to group overlapping tasks
            const posKey = `${startPosition}-${width}`;
            if (!taskPositions[posKey]) {
              taskPositions[posKey] = [];
            }
            taskPositions[posKey].push({
              task: task,
              source: 'product',
              initialDisplay: 'block'
            });
          }
        }
      });
    }
    
    // Render tasks with vertical offsets to prevent overlapping
    Object.keys(taskPositions).forEach(posKey => {
      const [startPosition, width] = posKey.split('-').map(Number);
      const tasks = taskPositions[posKey];
      
      // Sort tasks by start date to ensure consistent ordering
      tasks.sort((a, b) => {
        const dateA = new Date(a.task.start);
        const dateB = new Date(b.task.start);
        return dateA - dateB;
      });
      
      // Calculate optimal vertical spacing based on number of tasks
      const taskHeight = 25; // Base height of a task
      const verticalPadding = 5; // Padding between tasks
      
      tasks.forEach((taskObj, index) => {
        const task = taskObj.task;
        // Determine the class based on status and funding type
        let statusClass = task.status.toLowerCase().replace(/\s+/g, '-');
        if (task.fundingType) {
          statusClass += ` funding-${task.fundingType.toLowerCase().replace(/\s+/g, '-')}`;
        }
        
        // Add material-specific class if it's from a material system
        let materialClass = '';
        if (taskObj.source === 'material') {
          materialClass = ` material-specific material-task-${taskObj.materialId}`;
        }
        
        // Calculate vertical position with better spacing
        const verticalOffset = index * (taskHeight + verticalPadding);
        
        // Create a source indicator for the tooltip
        const sourceText = taskObj.source === 'material' ? 
          `[Material: ${roadmapData.materialSystems.find(ms => ms.id === taskObj.materialId)?.name || taskObj.materialId}] ` : 
          '';
        
        // For the display label, put the task name first, then the source in parentheses
        const displayLabel = taskObj.source === 'material' ? 
          `${task.task} (${roadmapData.materialSystems.find(ms => ms.id === taskObj.materialId)?.name || taskObj.materialId})` : 
          task.task;
        
        // Add display style based on initialDisplay property
        const displayStyle = taskObj.initialDisplay || 'block';
        
        html += `
          <div class="roadmap-task ${statusClass}${materialClass}" 
               style="left: ${startPosition}px; width: ${width}px; top: ${verticalOffset}px; height: ${taskHeight}px; display: ${displayStyle};"
               title="${sourceText}${task.task}: ${formatDate(task.start)} - ${formatDate(task.end)}${task.fundingType ? ' | Funding: ' + task.fundingType : ''}"
               data-source="${taskObj.source}" 
               ${taskObj.materialId ? `data-material-id="${taskObj.materialId}"` : ''}>
            <div class="task-label">${displayLabel}</div>
          </div>`;
      });
    });
    
    html += `</div>
      </div>`;
  });
  
  html += `</div>`;
  
  // Add color key
  html += `
    <div class="roadmap-key">
      <h4>Roadmap Key</h4>
      <div class="key-items">
        <div class="key-item">
          <div class="key-color planned"></div>
          <div class="key-label">Planned</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-sector-irad"></div>
          <div class="key-label">In Development (Sector IRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-division-irad"></div>
          <div class="key-label">In Development (Division IRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-crad"></div>
          <div class="key-label">In Development (CRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color complete"></div>
          <div class="key-label">Complete</div>
        </div>
      </div>
      <p class="roadmap-source-note">Roadmap tasks are sourced from the product's roadmap data and the selected material system.</p>
    </div>`;
  
  container.innerHTML = html;
  
  // Adjust row heights based on content
  adjustRowHeights(container);
  
  // Add event listener for the date picker
  const datePicker = container.querySelector('.start-date-picker');
  if (datePicker) {
    datePicker.addEventListener('change', function() {
      renderProductRoadmap(product, containerId, this.value, roadmapData);
    });
  }
  
  // Add event listeners to tasks for showing task details
  const tasks = container.querySelectorAll('.roadmap-task');
  tasks.forEach(taskElement => {
    taskElement.addEventListener('click', function() {
      const source = this.getAttribute('data-source');
      const materialId = this.getAttribute('data-material-id');
      
      // Find the task data
      const taskLabel = this.querySelector('.task-label').textContent;
      const taskName = taskLabel.includes('(') ? taskLabel.split('(')[0].trim() : taskLabel;
      
      let taskData;
      if (source === 'material' && materialId) {
        const material = roadmapData.materialSystems.find(ms => ms.id === materialId);
        if (material && material.roadmap) {
          taskData = material.roadmap.find(t => t.task === taskName);
        }
      } else {
        if (product.roadmap) {
          taskData = product.roadmap.find(t => t.task === taskName);
        }
      }
      
      if (taskData) {
        loadTaskDetails(taskData, source, materialId, roadmapData);
      }
    });
  });
}

/**
 * Loads task details into the task detail view
 * @param {Object} task - The task object
 * @param {string} source - The source of the task ('material' or 'product')
 * @param {string} materialId - The material ID if source is 'material'
 * @param {Object} roadmapData - The complete roadmap data
 */
function loadTaskDetails(task, source, materialId, roadmapData) {
  // Create a new detail section for task details
  const detail = document.getElementById("taskDetailSection") || createTaskDetailSection();
  
  // Store the current view in navigation stack BEFORE changing views
  navStack.push("productDetailSection");
  
  // Determine the source text and additional info based on where the task came from
  let sourceText = '';
  
  if (source === 'material') {
    const material = roadmapData.materialSystems.find(ms => ms.id === materialId);
    sourceText = `<p><strong>Source:</strong> Material System - ${material ? material.name : materialId}</p>`;
  } else {
    sourceText = `<p><strong>Source:</strong> Product Roadmap</p>`;
  }
  
  // Build the HTML content
  let html = `
    <h2>Task Details: ${task.task}</h2>
    ${sourceText}
    <div class="task-details-grid">
      <div class="task-detail-item">
        <strong>Start Date:</strong> ${formatDate(task.start)}
      </div>
      <div class="task-detail-item">
        <strong>End Date:</strong> ${formatDate(task.end)}
      </div>
      <div class="task-detail-item">
        <strong>Status:</strong> ${task.status}
      </div>`;
  
  // Add funding type if available
  if (task.fundingType) {
    html += `
      <div class="task-detail-item">
        <strong>Funding Type:</strong> ${task.fundingType}
      </div>`;
  }
  
  // Add lane if available
  if (task.lane) {
    html += `
      <div class="task-detail-item">
        <strong>Category:</strong> ${task.lane}
      </div>`;
  }
  
  // Add any additional fields that might be in the task object
  for (const [key, value] of Object.entries(task)) {
    // Skip fields we've already displayed
    if (['task', 'start', 'end', 'status', 'fundingType', 'lane'].includes(key)) continue;
    
    html += `
      <div class="task-detail-item">
        <strong>${key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}:</strong> ${value}
      </div>`;
  }
  
  html += `</div>
    <button class="back-button" onclick="goBack()">Back</button>`;
  
  // Set the HTML content
  detail.innerHTML = html;
  
  // Hide all main and detail views before showing this detail view
  document.querySelectorAll(".main-view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".detail-view").forEach(d => d.classList.remove("active"));
  detail.classList.add("active");
}

module.exports = {
  updateRoadmapMaterialTasks,
  renderProductRoadmap,
  loadTaskDetails
}; 